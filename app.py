"""
Main Flask application file
- Initializes Flask app and extensions (SocketIO, JWT, Bcrypt)
- Registers routes and error handlers
- Configures WebSocket events
- Sets up database connection
""" 

from flask import Flask
from flask_socketio import SocketIO
from database import init_db

app = Flask(__name__)
socketio = SocketIO(app)
db = init_db(app)

@app.route('/')
def index():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(debug=True)

