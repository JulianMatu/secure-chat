"""
Database setup and operations
- Initializes SQLite database
- Provides functions for user management
- Handles chat session operations
- Manages online status tracking
""" 

from flask_sqlalchemy import SQLAlchemy

# Initialize database
def init_db(app):
    db = SQLAlchemy(app)
    return db

