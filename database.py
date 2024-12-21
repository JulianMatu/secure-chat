"""
Database setup and operations
- Initializes SQLite database
- Provides functions for user management
- Handles chat session operations
- Manages online status tracking
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import click

db = SQLAlchemy()

## Database Models ##

# Users Table
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    public_key_rsa = db.Column(db.String, nullable=False)
    public_key_dsa = db.Column(db.String, nullable=False)
    is_online = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    signature_preference = db.Column(
        db.Enum('RSA', 'DSA', name='signature_preference_enum'),
        default='RSA',
        nullable=False
    )

    # Relationships
    chat_participations = db.relationship('ChatParticipant', backref='user', lazy=True)
    sent_messages = db.relationship('Message', backref='sender', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

# Chat Sessions Table
class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    name = db.Column(db.String, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    encrypted_symmetric_key = db.Column(db.String, nullable=False) # Encrypted with the server's Master key

    # Relationships
    participants = db.relationship('ChatParticipant', backref='chat_session', lazy=True)
    messages = db.relationship('Message', backref='chat_session', lazy=True)

    def __repr__(self):
        return f"<ChatSession {self.id} at {self.created_at}>"

# Chat Participants Table
class ChatParticipant(db.Model):
    __tablename__ = 'chat_participants'

    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True, nullable=False)

    def __repr__(self):
        return f"<ChatParticipant User {self.user_id} in Session {self.session_id}>"

# Messages Table
# Content is encrypted with E2E Symmetric Key
class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)  # Encrypted message content
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Message {self.id} in Session {self.session_id} from User {self.sender_id}>"

# Returns HTML-formatted string containing all database contents
def database_to_html(db) -> str:
    html = "<html><body>"

    # Users Table
    html += "<h2>Users</h2><table border='1'><tr><th>ID</th><th>Username</th><th>Is Online</th><th>Created At</th><th>RSA Public Key</th><th>DSA Public Key</th></tr>"
    for user in User.query.all():
        html += f"<tr><td>{user.id}</td><td>{user.username}</td><td>{user.is_online}</td><td>{user.created_at}</td><td>{user.public_key_rsa}</td><td>{user.public_key_dsa}</td></tr>"
    html += "</table>"

    # Chat Sessions Table
    html += "<h2>Chat Sessions</h2><table border='1'><tr><th>ID</th><th>Name</th><th>Owner ID</th><th>Created At</th><th>Encrypted Symmetric Key</th></tr>"
    for session in ChatSession.query.all():
        html += f"<tr><td>{session.id}</td><td>{session.name}</td><td>{session.owner_id}</td><td>{session.created_at}</td><td>{session.encrypted_symmetric_key}</td></tr>"
    html += "</table>"

    # Chat Participants Table
    html += "<h2>Chat Participants</h2><table border='1'><tr><th>Session ID</th><th>User ID</th></tr>"
    for participant in ChatParticipant.query.all():
        html += f"<tr><td>{participant.session_id}</td><td>{participant.user_id}</td></tr>"
    html += "</table>"

    # Messages Table
    html += "<h2>Messages</h2><table border='1'><tr><th>ID</th><th>Session ID</th><th>Sender ID</th><th>Content</th><th>Created At</th></tr>"
    for message in Message.query.all():
        html += f"<tr><td>{message.id}</td><td>{message.session_id}</td><td>{message.sender_id}</td><td>{message.content}</td><td>{message.created_at}</td></tr>"
    html += "</table>"

    html += "</body></html>"
    return html

# Helper function for creating a new account in the database
def db_create_account(username: str, password_hash: str, \
                      public_key_rsa: str, public_key_dsa: str) -> bool:
    if db_check_account(username) is not None:
        print("Username already exists.")
        return False
    user = User(username=username, password_hash=password_hash,\
                 public_key_rsa=public_key_rsa, public_key_dsa=public_key_dsa)
    db.session.add(user)
    db.session.commit()
    return True

# Takes a username and returns the corresponding User object
def db_check_account(username: str):
    return User.query.filter_by(username=username).first()

# Get user by ID
def db_get_user_by_id(user_id: int):
    return User.query.get(user_id)

# Get all users
def db_get_all_users():
    return User.query.all()

# Updates the online status of the given user
def db_update_online_status(user_id: int, is_online: bool):
    user = User.query.get(user_id)
    user.is_online = is_online
    db.session.commit()

# Update user's public key
def db_update_public_key(user_id: int, public_key_rsa: str, public_key_dsa: str):
    user = db_get_user_by_id(user_id)
    user.public_key_rsa = public_key_rsa
    user.public_key_dsa = public_key_dsa
    db.session.commit()

# Creates a new empty chat session
# Chats must have a owner and a name
def db_create_chat_session(name: str, owner_id: int, encrypted_symmetric_key: str) -> ChatSession:
    session = ChatSession(name=name, owner_id=owner_id, encrypted_symmetric_key=encrypted_symmetric_key)
    db.session.add(session)
    db.session.commit()
    return session

# Returns the chat session with the given ID
def db_get_chat_session(session_id: int) -> ChatSession:
    return ChatSession.query.get(session_id)

def db_get_chat_session_encrypted_symmetric_key(session_id: int) -> str:
    return db_get_chat_session(session_id).encrypted_symmetric_key

# Adds a user to a chat session
def db_add_chat_participant(session_id: int, user_id: int):
    if ChatParticipant.query.filter_by(session_id=session_id, user_id=user_id).first() is not None:
        return None
    participant = ChatParticipant(session_id=session_id, user_id=user_id)
    db.session.add(participant)
    db.session.commit()
    return participant

# Removes a user from a chat session
def db_remove_chat_participant(session_id: int, user_id: int):
    participant = ChatParticipant.query.filter_by(session_id=session_id, user_id=user_id).first()
    if participant is None:
        return None
    db.session.delete(participant)
    db.session.commit()
    return participant

# Returns all User objects that are participants in a given chat session
def db_get_chat_session_users(session_id: int) -> list:
    participants = ChatParticipant.query.filter_by(session_id=session_id).all()
    users = []
    for participant in participants:
        users.append(db_get_user_by_id(participant.user_id))
    return users

# Creates a new message in the given chat session
def db_create_message(session_id: int, sender_id: int, content: str) -> Message:
    message = Message(session_id=session_id, sender_id=sender_id, content=content)
    db.session.add(message)
    db.session.commit()
    return message

# Returns all messages in the given chat session, sorted by creation time
def db_get_messages(session_id: int) -> list:
    messages = Message.query.filter_by(session_id=session_id).order_by(Message.created_at).all()
    click.echo(f'Messages for session {session_id}: {messages}')
    return messages

# Returns all chat sessions the given user is a part of
def db_get_user_chat_sessions(user_id: int) -> list:
    participants = ChatParticipant.query.filter_by(user_id=user_id).all()
    sessions = []
    for participant in participants:
        sessions.append(db_get_chat_session(participant.session_id))
    return sessions