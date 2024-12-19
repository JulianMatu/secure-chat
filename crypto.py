"""
Cryptographic utilities
- RSA/DSA key generation and management
- AES encryption/decryption functions
- Digital signature operations
- Key distribution helpers
""" 

from bcrypt import hashpw, gensalt, checkpw
from Crypto.Cipher import AES
from Crypto.Hash import SHA256

# Hash Password
def hash_password(password: str) -> str:
    return hashpw(password.encode(), gensalt()).decode()

# Check Password
def check_password(password: str, password_hash: str) -> bool:
    return checkpw(password.encode(), password_hash.encode())