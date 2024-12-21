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
from Crypto.PublicKey import RSA, ECC
from Crypto.Signature import DSS
from Crypto.Random import get_random_bytes
import base64

# Hash Password
def hash_password(password: str, pepper: bytes) -> str:
    return hashpw(password.encode() + pepper, gensalt()).decode()

# Check Password
def check_password(password: str, pepper: bytes, password_hash: str) -> bool:
    return checkpw(password.encode() + pepper, password_hash.encode())

# Generate a symmetric key for 256-bit AES encryption
def generate_symmetric_key() -> bytes:
    return base64.b64encode(get_random_bytes(32))

# Encrypt with AES
def encrypt_AES(message: bytes, key: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(message)
    return base64.b64encode(cipher.nonce + tag + ciphertext)

# Decrypt with AES
# In regular bytes format
def decrypt_AES(ciphertext: str, key: bytes) -> bytes:
    ciphertext = base64.b64decode(ciphertext)
    nonce = ciphertext[:16]
    tag = ciphertext[16:32]
    ciphertext = ciphertext[32:]
    cipher = AES.new(key, AES.MODE_GCM, nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)

# Encrypt Key with RSA
# Outputs a base64 encoded string
def encrypt_key_RSA(key: bytes, public_key: str) -> str:
    public_key = RSA.import_key(base64.b64decode(public_key))
    cipher = PKCS1_OAEP.new(public_key, hashAlgo=SHA256)
    return base64.b64encode(cipher.encrypt(key)).decode()

# Decrypt Key with RSA
def decrypt_key_RSA(key: str, private_key: str) -> bytes:
    private_key = RSA.import_key(base64.b64decode(private_key))
    cipher = PKCS1_OAEP.new(private_key, hashAlgo=SHA256)
    return cipher.decrypt(base64.b64decode(key))