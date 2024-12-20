"""
Cryptographic utilities
- RSA/DSA key generation and management
- AES encryption/decryption functions
- Digital signature operations
- Key distribution helpers
""" 

from bcrypt import hashpw, gensalt, checkpw
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA, DSA
from Crypto.Random import get_random_bytes
import base64

# Hash Password
def hash_password(password: str) -> str:
    return hashpw(password.encode(), gensalt()).decode()

# Check Password
def check_password(password: str, password_hash: str) -> bool:
    return checkpw(password.encode(), password_hash.encode())

# Generate a symmetric key for 256-bit AES encryption
def generate_symmetric_key() -> bytes:
    return get_random_bytes(32)

# Encrypt with AES
def encrypt_AES(message: bytes, key: bytes) -> str:
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(message)
    return base64.b64encode(cipher.nonce + tag + ciphertext).decode()

# Decrypt with AES
def decrypt_AES(ciphertext: str, key: bytes) -> bytes:
    ciphertext = base64.b64decode(ciphertext)
    nonce = ciphertext[:16]
    tag = ciphertext[16:32]
    ciphertext = ciphertext[32:]
    cipher = AES.new(key, AES.MODE_GCM, nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)

# Encrypt Key with RSA
def encrypt_key_RSA(key: bytes, public_key: bytes) -> str:
    public_key = RSA.import_key(public_key)
    cipher = PKCS1_OAEP.new(public_key)
    return base64.b64encode(cipher.encrypt(key)).decode()

# Encrypt Key with DSA
def encrypt_key_DSA(key: bytes, public_key: bytes) -> str:
    public_key = DSA.import_key(public_key)
    cipher = PKCS1_OAEP.new(public_key)
    return cipher.encrypt(key).decode()