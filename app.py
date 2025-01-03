"""
Main Flask application file
- Initializes Flask app and extensions
- Registers routes and error handlers
- Configures WebSocket events
- Sets up database connection
""" 

from flask import Flask, redirect, url_for, session, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from functools import wraps
from database import *
from crypto import *
from dotenv import load_dotenv
import os
import sys
import click
import base64

# Load environment variables
load_dotenv()
MASTER_KEY = base64.b64decode(os.getenv('MASTER_KEY'))
PEPPER = base64.b64decode(os.getenv('PEPPER'))
CHAT_ROOM_LIMIT = 5
ssl_cert_path = os.getenv('SSL_CERT_PATH')
ssl_key_path = os.getenv('SSL_KEY_PATH')
PORT = os.getenv('PORT')
HOST = os.getenv('HOST')
DEBUG = (os.getenv('DEBUG') == 'True')

## Configuration ##
app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = os.urandom(24) # Required for session management

WIN = sys.platform.startswith('win')
prefix = 'sqlite:///' if WIN else 'sqlite:////'

app.config['SQLALCHEMY_DATABASE_URI'] = prefix + 'securechat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()

## Authentication Decorators for Flask and SocketIO ##
def login_required_flask(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def login_required_socketio(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return
        return f(*args, **kwargs)
    return decorated_function

## HTML Page Routes ##
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('chat', session_id=session['user_id']))
    else:
        return redirect(url_for('login'))

@app.route('/login')
def login():
    if 'user_id' in session:
        return redirect(url_for('chat'))
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/chat')
@login_required_flask
def chat():
    return render_template('chat.html')

## Web Socket Event Handlers ##
# When a user connects, update their online status
# And tell clients to requery the chat rooms they are in
@socketio.on('connect')
@login_required_socketio
def handle_connect():
    user_id = session['user_id']
    if not user_id:
        return
    else:
        db_update_online_status(user_id, True)
        for room in db_get_user_chat_sessions(session['user_id']):
            emit('requery_room', room=room.id)

# When a user disconnects, update their online status
# And tell clients to requery the chat rooms they are in
@socketio.on('disconnect')
@login_required_socketio
def handle_disconnect():
    user_id = session['user_id']
    if not user_id:
        return
    else:
        db_update_online_status(user_id, False)
        for room in db_get_user_chat_sessions(session['user_id']):
            emit('requery_room', room=room.id)

# Add a user to a chat room
# Only the owner of the chat room can add users
@socketio.on('add_user_to_chat')
@login_required_socketio
def handle_add_user_to_chat(data):
    room_id = data['room_id']
    user_id = data['user_id']
    chat_session = db_get_chat_session(room_id)
    if chat_session.owner_id != session['user_id']:
        return
    db_add_chat_participant(room_id, user_id)
    emit('requery_room', room=room_id)

# Remove a user from a chat room
# Any user can remove themselves from a chat room
@socketio.on('remove_user_from_chat')
@login_required_socketio
def handle_remove_user_from_chat(data):
    room_id = data['room_id']
    user_id = data['user_id']
    if user_id != session['user_id'] and user_id != db_get_chat_session(room_id).owner_id:
        return
    if db_remove_chat_participant(room_id, user_id):
        emit('requery_room', room=room_id)

# Send a message to a chat room
@socketio.on('send_message_to_room')
@login_required_socketio
def handle_send_message_to_room(data):
    room_id = data['room_id']
    user_id = data['user_id']
    message = data['message']
    rsa_signature = data['rsa_signature']
    dsa_signature = data['dsa_signature']
    db_create_message(room_id, user_id, message, rsa_signature, dsa_signature)
    emit('requery_room', room=room_id)

# Create a new chat room and add the owner as a participant
@socketio.on('create_chat_room')
@login_required_socketio
def handle_create_chat_room(data):
    rooms = db_get_user_chat_sessions(session['user_id'])
    if len(rooms) >= CHAT_ROOM_LIMIT:
        click.echo(f"User {session['user_id']} has reached the chat room limit")
        return
    symm_key = generate_symmetric_key()
    click.echo(f"Symmetric key: {symm_key.decode()} for chat session {data['chat_name']}")
    enc_key = encrypt_AES(symm_key, MASTER_KEY)
    click.echo(f"Encrypted symmetric key: {enc_key.decode()} for chat session {data['chat_name']}")
    chat_session = db_create_chat_session(name=data['chat_name'], owner_id=session['user_id'], encrypted_symmetric_key=enc_key.decode())
    db_add_chat_participant(session_id=chat_session.id, user_id=session['user_id'])
    emit('chat_created', {"room_id": chat_session.id})

# Join a chat room
@socketio.on('join_room')
@login_required_socketio
def handle_join_room(data):
    room_id = data['room_id']
    join_room(room_id)
    emit('requery_room', room=room_id)

# Leave a chat room
@socketio.on('leave_room')
@login_required_socketio
def handle_leave_room(data):
    room_id = data['room_id']
    leave_room(room_id)
    emit('requery_room', room=room_id)

# Sends all information about a chat room to the client
@socketio.on('query_chat_room')
@login_required_socketio
def handle_query_chat_room(data):
    room_id = data['room_id']
    session_users = db_get_chat_session_users(room_id)
    session_messages = db_get_messages(room_id)
    encrypted_session_key = db_get_chat_session_encrypted_symmetric_key(room_id)
    user = db_get_user_by_id(session['user_id'])
    unencrypted_session_key = decrypt_AES(encrypted_session_key, MASTER_KEY)
    user_encrypted_key = encrypt_key_RSA(base64.b64decode(unencrypted_session_key), user.public_key_rsa)
    payload= {
        "room_id": room_id, 
        "room_name": db_get_chat_session(room_id).name,
        "participants": [{"id": user.id, "username": user.username, "is_online": user.is_online, "rsa_public_key": user.public_key_rsa, "dsa_public_key": user.public_key_dsa} for user in session_users] if session_users else [],
        "messages": [{"id": msg.id, "sender_id": msg.sender_id, "created_at": str(msg.created_at.strftime('%m-%d %H:%M:%S')),\
                       "content": msg.content, "signatures": {"RSA": msg.rsa_signature, "DSA": msg.dsa_signature}} for msg in session_messages] if session_messages else [],
        "   ": user_encrypted_key,
    }
    emit('res_query_chat_room', payload)

# Sends all chat rooms the user is a part of
@socketio.on('query_user_chat_rooms')
@login_required_socketio
def handle_query_user_chat_rooms():
    rooms = db_get_user_chat_sessions(session['user_id'])
    emit('res_query_user_chat_rooms', {
        "chat_rooms": [{"id": room.id, "name": room.name} for room in rooms],
    })

# Allows any user to query their own ID
@socketio.on('query_user_id')
@login_required_socketio
def handle_query_user_id():
    emit('res_query_user_id', {
        "user_id": session['user_id'],
    })

# Allows any user to query another user's ID by username, even if they are not in the same chat room
@socketio.on('query_user_by_username')
@login_required_socketio
def handle_query_user_by_username(data):
    user = db_check_account(data['username'])
    if user:
        emit('res_query_user_by_username', {
            "user_id": user.id,
            "username": user.username,
        })
    else:
        emit('res_query_user_by_username', {
            "user_id": -1,
            "username": data['username'],
        })
                
## API Routes ##
@app.route('/api/register', methods=['POST'])
def register_api():
    username = request.form['username']
    password = request.form['password']
    rsakey = ""
    dsakey = ""
    
    # Check if username already exists
    user = db_check_account(username)
    if user is not None:
        return "Username already exists", 401
    
    # Hash password
    hashed_password = hash_password(password, PEPPER)

    db_create_account(username=username, password_hash=hashed_password,\
                       public_key_rsa=rsakey, public_key_dsa=dsakey)
    
    return "Registration successful", 200

@app.route('/api/login', methods=['POST'])
def login_api():
    username = request.form['username']
    password = request.form['password']
    rsakey = request.form['rsaPublicKey']
    dsakey = request.form['dsaPublicKey']
    
    # Grab user from database
    user = db_check_account(username)
    if user and check_password(password, PEPPER, user.password_hash):
        session['user_id'] = user.id
        db_update_public_key(user.id, rsakey, dsakey)
        return "Login successful", 200
    else:
        return "Invalid credentials", 401
    
@app.route('/api/logout', methods=['POST'])
def logout_api():
    if 'user_id' in session:
        for room in db_get_user_chat_sessions(session['user_id']):
            socketio.emit('requery_room', room=room.id)
        session.clear()
    return "Logout Successful", 200

## Debug Routes ##
if DEBUG:
    @app.route('/database')
    def database():
        return database_to_html(db)

if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear')
    ssl_context = (ssl_cert_path, ssl_key_path) if ssl_cert_path and ssl_key_path else None
    click.echo(f"Server started. Connect to {HOST}:{PORT}")
    if ssl_context:
        socketio.run(app, host=HOST, port=PORT, debug=DEBUG, ssl_context=ssl_context)
    else:
        click.echo("SSL certificate and key not found. Running in insecure (HTTP) mode.")
        socketio.run(app, host=HOST, port=PORT, debug=DEBUG)