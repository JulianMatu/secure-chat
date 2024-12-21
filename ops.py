'''
This file contains functions that are used to 
recalculate password hashes and encrypted symmetric keys for all users and chat sessions in the database.
Use these functions whenever the pepper or master key is changed.
Master keys should be regularly rotated for security purposes.

'''
from app import app, db
from database import db_get_all_users, db_update_public_key, db_get_all_chat_sessions, db_update_chat_session_key
from crypto import hash_password, encrypt_AES, generate_symmetric_key
import os
import base64

# Load environment variables
from dotenv import load_dotenv
load_dotenv()
PEPPER = base64.b64decode(os.getenv('PEPPER'))
MASTER_KEY = base64.b64decode(os.getenv('MASTER_KEY'))

def recalculate_password_hashes():
    users = db_get_all_users()
    for user in users:
        new_hash = hash_password(user.password_hash, PEPPER)
        user.password_hash = new_hash
        print(f"Updated password hash for user {user.username}")

def recalculate_encrypted_symmetric_keys():
    sessions = db_get_all_chat_sessions()
    for session in sessions:
        new_key = generate_symmetric_key()
        encrypted_key = encrypt_AES(new_key, MASTER_KEY)
        db_update_chat_session_key(session.id, encrypted_key.decode())
        print(f"Updated encrypted symmetric key for chat session {session.name}")

def purge_database():
    with app.app_context():
        db.drop_all()
    
purge_database()