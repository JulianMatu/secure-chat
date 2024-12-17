-- Database schema

-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    public_key_rsa TEXT NOT NULL,
    public_key_dsa TEXT NOT NULL,
    is_online BOOLEAN DEFAULT 0,
    signature_preference TEXT DEFAULT 'RSA'
        CHECK(signature_preference IN ('RSA', 'DSA'))
);

-- Chat sessions table
CREATE TABLE chat_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat participants table
CREATE TABLE chat_participants (
    session_id INTEGER,
    user_id INTEGER,
    encrypted_symmetric_key TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    PRIMARY KEY (session_id, user_id)
); 

-- Messages table
-- Content is encrypted with E2E Symmetric Key
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    sender_id INTEGER,
    content TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id),
    FOREIGN KEY (sender_id) REFERENCES users(id)
);
