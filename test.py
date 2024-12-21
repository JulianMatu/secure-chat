import unittest
import base64
from crypto import (
    generate_symmetric_key, encrypt_AES, decrypt_AES,
    encrypt_key_RSA, decrypt_key_RSA
)
from Crypto.PublicKey import RSA

class TestCrypto(unittest.TestCase):

    def test_generate_symmetric_key(self):
        key = generate_symmetric_key()
        self.assertEqual(len(key), 44)  # 32 bytes base64 encoded

    def test_encrypt_decrypt_AES(self):
        key = generate_symmetric_key()
        message = b"Secret Message"
        ciphertext = encrypt_AES(message, base64.b64decode(key))
        decrypted_message = decrypt_AES(ciphertext, base64.b64decode(key))
        self.assertEqual(message, decrypted_message)

    def test_encrypt_key_RSA(self):
        key = generate_symmetric_key()
        rsa_key = RSA.generate(2048)
        public_key = rsa_key.publickey().export_key()
        encrypted_key = encrypt_key_RSA(base64.b64decode(key), public_key)
        self.assertIsInstance(encrypted_key, str)

    def test_rsa_encryption_decryption(self):
        # Generate a symmetric key
        symmetric_key = generate_symmetric_key()
        
        # Generate RSA key pair
        rsa_key = RSA.generate(2048)
        public_key_pem = rsa_key.publickey().export_key()
        private_key_pem = rsa_key.export_key()
        
        # Encrypt the symmetric key with the public RSA key
        encrypted_key = encrypt_key_RSA(base64.b64decode(symmetric_key), public_key_pem)
        
        # Decrypt the symmetric key with the private RSA key
        decrypted_key = decrypt_key_RSA(encrypted_key, private_key_pem)
        
        # Check if the decrypted key matches the original symmetric key
        self.assertEqual(base64.b64encode(decrypted_key), symmetric_key)

if __name__ == '__main__':
    unittest.main()
