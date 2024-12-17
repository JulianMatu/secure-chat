"""
Main Flask application file
- Initializes Flask app and extensions (SocketIO, JWT, Bcrypt)
- Registers routes and error handlers
- Configures WebSocket events
- Sets up database connection
""" 

from flask import Flask
from flask_socketio import SocketIO
from database import init_db, database_to_html

app = Flask(__name__)
socketio = SocketIO(app)
db = init_db(app)

## HTML Page Routes ##
@app.route('/')
def index():
    return "Hello, World!"

@app.route('/login')
def login():
    # TODO: Check if user is already logged in
    return "/static/login.html"

@app.route('/register')
def register():
    return "Register page"

@app.route('/chat/<int:session_id>')
def chat(session_id):
    return "Chat page"

## API Routes ##
@app.route('/api/register', methods=['POST'])
def register_api():
    return "Register API"

@app.route('/api/login', methods=['POST'])
def login_api():
    return "Login API"

@app.route('/api/users/online', methods=['GET'])
def users_online_api():
    return "Users Online API"

@app.route('/api/chat/create', methods=['POST'])
def chat_create_api():
    return "Chat Create API"

@app.route('/api/chat/invite', methods=['POST'])
def chat_invite_api():
    return "Chat Invite API"

@app.route('/api/chat/leave', methods=['POST'])
def chat_leave_api():
    return "Chat Leave API"

@app.route('/api/chat/messages', methods=['GET'])
def chat_messages_api():
    return "Chat Messages API"

## Debug Routes ##
if app.config['DEBUG']:
    @app.route('/database')
    def database():
        return database_to_html(db)

if __name__ == '__main__':
    app.run(debug=True)
    app.logger.info(str(app.config))