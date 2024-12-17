"""
Database setup and operations
- Initializes SQLite database
- Provides functions for user management
- Handles chat session operations
- Manages online status tracking
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# Initialize database including schema
def init_db(app):
    # Configure database settings
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///secure-chat.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize SQLAlchemy
    db = SQLAlchemy(app)

    # Users Table
    class User(db.Model):
        __tablename__ = 'users'

        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        username = db.Column(db.String, unique=True, nullable=False)
        password_hash = db.Column(db.String, nullable=False)
        public_key_rsa = db.Column(db.String, nullable=False)
        public_key_dsa = db.Column(db.String, nullable=False)
        is_online = db.Column(db.Boolean, default=False)
        created_at = db.Column(db.DateTime, default=datetime.now(datetime.timezone.utc))
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
        created_at = db.Column(db.DateTime, default=datetime.now(datetime.timezone.utc))

        # Relationships
        participants = db.relationship('ChatParticipant', backref='chat_session', lazy=True)
        messages = db.relationship('Message', backref='chat_session', lazy=True)

        def __repr__(self):
            return f"<ChatSession {self.id} at {self.created_at}>"

    # Chat Participants Table
    class ChatParticipant(db.Model):
        __tablename__ = 'chat_participants'

        session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
        encrypted_symmetric_key = db.Column(db.String, nullable=False)

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
        created_at = db.Column(db.DateTime, default=datetime.now(datetime.timezone.utc))

        def __repr__(self):
            return f"<Message {self.id} in Session {self.session_id} from User {self.sender_id}>"
        
    return db

