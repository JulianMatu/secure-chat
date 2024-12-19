# Secure Chat Requirements

## Core Requirements

* Users must be registered with the chat server.
* Users authenticate with username and password.
* Server verifies credentials and updates user status to "online".
* Users can specify multiple users to chat with.
* Users can check which other users are online.
* Users can invite online users to ongoing conversations.
* Server generates and distributes symmetric keys securely.
* Symmetric keys are encrypted using users' public keys.
* Users are notified if invited participants are offline.
* Users decrypt symmetric key with their private key to join chat.
* All chat messages must be encrypted with the symmetric key.
* Users can leave conversations at will.
* User status changes to "offline" upon disconnection.
* Online status checking must be available.
* Single chat session support is sufficient.
* Must provide both confidentiality and digital signatures.
* Must support both RSA and DSA digital signature schemes.
* Users must use both signatures
* Must follow best practices for Web Security.

## System Architecture

### Tech Stack
- Backend: Flask + Python
- Database: SQLite (simple file-based database)
- Frontend: Plain HTML + JavaScript (no framework)
- WebSocket: Flask-SocketIO for real-time communication
- Cryptography: 
  - pycryptodome for RSA/DSA/AES encryption
  - Flask-JWT-Extended for JWT authentication
  - Flask-Bcrypt for password hashing

### Security Components
- JWT for session management
- RSA (2048-bit) for digital signatures and authentication
- DSA (2048-bit) for digital signatures and authentication
- AES-256-GCM for end-to-end message encryption
- Bcrypt for password hashing

### Encryption Flow
1. End-to-End Message Encryption
   - All messages encrypted with AES-256-GCM
   - Each chat session has unique AES key
   - AES keys never transmitted in plaintext
   
2. Authentication & Key Exchange
   - Each user maintains both RSA and DSA keypairs
   - RSA keypair:
     - Used for encrypting/decrypting AES session keys
     - Used for user authentication to server
   - DSA keypair:
     - Used for message signing and verification
     - Used for user-to-user authentication
   - Users can switch between RSA/DSA for message signatures

3. Key Distribution
   - Server never has access to:
     - Private keys (RSA or DSA)
     - Decrypted messages
     - Decrypted AES session keys
   - AES session keys encrypted with recipient's RSA public key
   - Each recipient gets their own encrypted copy of AES key

### API Endpoints
- POST /auth/register
- POST /auth/login
- GET /users/online
- POST /chat/create
- POST /chat/invite
- POST /chat/leave
- WebSocket endpoint for real-time messages

### Data Flow
1. User Registration/Login
   - Register with username/password
   - Generate RSA and DSA key pair
   - Store public key, hash private key
   
2. Chat Session Creation
   - Generate AES symmetric key
   - Encrypt with participants' public keys
   - Store encrypted keys in database
   
3. Message Exchange
   - Encrypt message with symmetric key
   - Sign with sender's private key
   - Send via WebSocket
   - Recipients verify signature and decrypt

### Security Considerations
- All HTTP endpoints use HTTPS
- WebSocket connections are secure (WSS)
- No storage of private keys on server
- Symmetric keys unique per chat session
- Session tokens expire after inactivity