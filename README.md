# Secure Chat Requirements

* In this project, you are to implement a system that enables a group of users to chat securely.
* All users are registered with the chat server.
* When the user wants to chat with another registered user, they first connect to the chat server and enter their username and password.
* The server verifies the username and password, and if correct, the user’s status is changed to “online”.
* Next, the user may enter the user IDs of users with whom they wish to chat (could be more than one).
* At any given time, the user should be able to check which other users are online and invite them to the ongoing conversation.
* Once the user specifies the users with whom they wish to chat, the server generates a symmetric key and securely distributes it to all the specified users and the user who initiated the chat.
* To achieve secure key distribution, you must encrypt the symmetric key using the public keys of the respective users (you may assume that the server knows the public keys of all users).
* If one of the specified users is not online, the requesting user is notified about this.
* After the encrypted symmetric key has been distributed to all users, the users decrypt the symmetric key using their private keys, and the chat session may begin.
* All messages exchanged during the chat must be encrypted using the symmetric key provided by the server and must be delivered to all users participating in the chat.
* Any user may choose to leave the conversation.
* If the user disconnects from the chat server, their status should be changed to “offline”.
* All users who are connected to the server must have a way to check whether a given user is online.
* You do not need to support multiple chat sessions.
* Your implementation must provide both confidentiality and digital signature.
* For digital signatures, you must provide the user with a choice of using RSA or Digital Signature Algorithm (DSA; https://bit.ly/2TvvGSt).
* Both digital signature schemes must be supported.

# User Stories and Features

## User Stories

1. **User Registration**
   - As a user, I want to register with the chat server by providing a username and password, so that I can create an account.

2. **User Authentication**
   - As a user, I want to log in to the chat server using my username and password, so that I can access the chat system.

3. **Check Online Users**
   - As a user, I want to check which other users are online, so that I can invite them to a chat session.

4. **Initiate Chat Session**
   - As a user, I want to specify the user IDs of users I wish to chat with, so that I can start a secure chat session.

5. **Secure Key Distribution**
   - As a user, I want the server to generate a symmetric key for the chat session and securely distribute it to all specified users using their public keys, so that our communication is encrypted.

6. **Notify Offline Users**
   - As a user, I want to be notified if any specified user is not online, so that I can know who is available for the chat session.

7. **Decrypt Symmetric Key**
   - As a user, I want to decrypt the symmetric key using my private key, so that I can participate in the secure chat session.

8. **Send and Receive Encrypted Messages**
   - As a user, I want all messages exchanged during the chat to be encrypted using the symmetric key, so that our communication remains secure.

9. **Leave Conversation**
   - As a user, I want to be able to leave the conversation at any time, so that I can end my participation in the chat session.

10. **User Status**
    - As a user, I want my status to change to "offline" when I disconnect from the chat server, so that other users know I am not available.

11. **Digital Signature Choice**
    - As a user, I want to choose between RSA and Digital Signature Algorithm (DSA) for digital signatures, so that I can ensure message integrity and authentication.

## Features

1. **User Registration and Authentication**
   - Register and log in users with username and password.
   - Verify user credentials and update status to "online".

2. **Online User Check**
   - Display a list of online users.

3. **Chat Session Management**
   - Allow users to specify and invite other users to a chat session.
   - Notify users if any specified user is offline.

4. **Secure Key Distribution**
   - Generate and distribute symmetric keys securely using public keys.

5. **Message Encryption and Decryption**
   - Encrypt messages using the symmetric key.
   - Decrypt the symmetric key using private keys.

6. **User Status Management**
   - Update user status to "offline" upon disconnection.

7. **Digital Signature Support**
   - Provide options for RSA and DSA digital signatures.

# System Architecture

## Client-Server Model
The system follows a client-server model where the client is a web application and the server handles the core functionalities of the chat system.

### Client
- The client is a webpage that allows users to register, log in, and participate in secure chat sessions.
- It communicates with the server to authenticate users, check the status of other users, and send/receive encrypted messages.

### Server
- The server is responsible for user authentication, key management, and message distribution.
- It generates a symmetric key for each chat session and securely distributes it to the participants using their public keys.
- The server handles the distribution of encrypted messages but does not decrypt them, ensuring that all communication remains secure and private.

## Frameworks and Libraries

### Client
- **React**: A JavaScript library for building user interfaces.
- **Axios**: A promise-based HTTP client for making requests to the server.
- **CryptoJS**: A JavaScript library for performing cryptographic operations on the client side.

### Server
- **Node.js**: A JavaScript runtime for building scalable network applications.
- **Express**: A web application framework for Node.js, used to build the server.
- **jsonwebtoken**: A library to handle JSON Web Tokens (JWT) for user authentication.
- **bcrypt**: A library to hash and verify passwords.
- **crypto**: A built-in Node.js module for performing cryptographic operations.
- **mongoose**: An ODM (Object Data Modeling) library for MongoDB and Node.js.

## Security Frameworks and Libraries

### Client-Side
- **CryptoJS**: This JavaScript library is used for performing cryptographic operations on the client side. It provides various cryptographic algorithms such as AES for symmetric encryption, and SHA for hashing.

### Server-Side
- **jsonwebtoken**: This library is used to handle JSON Web Tokens (JWT) for user authentication. JWTs are used to securely transmit information between the client and server.
- **bcrypt**: This library is used to hash and verify passwords. It ensures that user passwords are stored securely in the database.
- **crypto**: This built-in Node.js module is used for performing cryptographic operations on the server side. It provides various cryptographic functionalities such as generating key pairs, encrypting/decrypting data, and creating digital signatures.

### Database
- **MongoDB**: A NoSQL database for storing user information, chat sessions, and messages.

### Key Management and Encryption
- **RSA and DSA**: The system supports both RSA and Digital Signature Algorithm (DSA) for digital signatures. These algorithms are used to provide digital signatures for message integrity and authentication.
- **Symmetric Key Encryption**: The server generates a symmetric key for each chat session and securely distributes it to the participants using their public keys. The symmetric key is used to encrypt and decrypt messages during the chat session.

These frameworks and libraries ensure that the chat system provides confidentiality, integrity, and authentication for secure communication.

### Setup
1. **Install MongoDB**: Follow the instructions on the [official MongoDB website](https://docs.mongodb.com/manual/installation/) to install MongoDB locally.
2. **Create a Database**: Create a new database for the chat system.
3. **Configure Mongoose**: Use Mongoose to connect to the MongoDB database in your server code. Define schemas and models for users, chat sessions, and messages.

Example Mongoose setup in `server.js`: