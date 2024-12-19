"""
Main Flask application file
- Initializes Flask app and extensions (SocketIO, JWT, Bcrypt)
- Registers routes and error handlers
- Configures WebSocket events
- Sets up database connection
""" 

from flask import Flask, redirect, url_for, session, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from functools import wraps
from database import *
from crypto import *
import os
import sys
import click

CHAT_ROOM_LIMIT = 5

app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = os.urandom(24) # Required for session management

## Configuration ##
WIN = sys.platform.startswith('win')
prefix = 'sqlite:///' if WIN else 'sqlite:////'

app.config['SQLALCHEMY_DATABASE_URI'] = prefix + 'securechat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()

## Authentication ##
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

# Choose which chat session to join or create a new one
@app.route('/chat')
@login_required_flask
def chat():
    return render_template('chat.html')

## Web Socket Event Handlers ##

# When a user connects, update their online status
@socketio.on('connect')
@login_required_socketio
def handle_connect():
    user_id = session['user_id']
    if not user_id:
        return
    else:
        db_update_online_status(user_id, True)

# When a user disconnects, update their online status
@socketio.on('disconnect')
@login_required_socketio
def handle_disconnect():
    user_id = session['user_id']
    if not user_id:
        return
    else:
        db_update_online_status(user_id, False)

# Add a user to a chat room
@socketio.on('add_user_to_chat')
@login_required_socketio
def handle_add_user_to_chat(data):
    room_id = data['room_id']
    user_id = data['user_id']
    chat_session = db_get_chat_session(room_id)
    # Check if user is the owner of the chat session
    if chat_session.owner_id != session['user_id']:
        return
    db_add_chat_participant(room_id, user_id, encrypted_symmetric_key="")
    emit('requery_room', room=room_id)

# Remove a user from a chat room
@socketio.on('remove_user_from_chat')
@login_required_socketio
def handle_remove_user_from_chat(data):
    room_id = data['room_id']
    user_id = data['user_id']
    if db_remove_chat_participant(room_id, user_id):
        emit('requery_room', room=room_id)

# Send a message to a chat room
@socketio.on('send_message_to_room')
@login_required_socketio
def handle_send_message_to_room(data):
    room_id = data['room_id']
    user_id = data['user_id']
    message = data['message']
    db_create_message(room_id, user_id, message)
    emit('requery_room', room=room_id)

# Create a new chat room and add the owner as a participant
@socketio.on('create_chat_room')
@login_required_socketio
def handle_create_chat_room(data):
    rooms = db_get_user_chat_sessions(session['user_id'])
    if len(rooms) >= CHAT_ROOM_LIMIT:
        return
    # Create chat session and add owner as participant
    # Symmetric key is blank for now
    chat_session = db_create_chat_session(name=data['chat_name'], owner_id=session['user_id'])
    db_add_chat_participant(session_id=chat_session.id, user_id=session['user_id'], encrypted_symmetric_key="")
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

    emit('res_query_chat_room', {
        "room_id": room_id, 
        "room_name": db_get_chat_session(room_id).name,
        "participants": [{"id": user.id, "username": user.username, "is_online": user.is_online} for user in session_users] if session_users else [],
        "messages": [{"id": msg.id, "sender_id": msg.sender_id, "created_at": str(msg.created_at), "content": msg.content} for msg in session_messages] if session_messages else [],
    })

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
    rsakey = 0#request.form['rsakey']
    dsakey = 0#request.form['dsakey']
    
    # Check if username already exists
    user = db_check_account(username)
    if user is not None:
        return redirect(url_for('register'))
    
    # Hash password
    hashed_password = hash_password(password)

    db_create_account(username=username, password_hash=hashed_password,\
                       public_key_rsa=rsakey, public_key_dsa=dsakey)
    
    return redirect(url_for('login'))


@app.route('/api/login', methods=['POST'])
def login_api():
    username = request.form['username']
    password = request.form['password']
    
    # Grab user from database
    user = db_check_account(username)
    if user and check_password(password, user.password_hash):
        session['user_id'] = user.id
        db_update_online_status(user.id, True) # Set user online when logged in
        return redirect(url_for('chat'))
    else:
        return redirect(url_for('login'))
    
@app.route('/api/logout', methods=['POST'])
def logout_api():
    if 'user_id' in session:
        db_update_online_status(session['user_id'], False)
        session.clear()
    return redirect(url_for('login'))

## Debug Routes ##
if __name__ == '__main__':
    @app.route('/database')
    def database():
        return database_to_html(db)

if __name__ == '__main__':
    socketio.run(app, debug=True)