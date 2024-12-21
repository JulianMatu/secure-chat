document.addEventListener('DOMContentLoaded', () => {
    const socket = io();  // Initialize Socket.IO

    // HTML elements
    const messageInput = document.getElementById('chat-input');
    const messagesList = document.getElementById('message-list');
    const userList = document.getElementById('user-list');
    const chatRoomsList = document.getElementById('chat-rooms');
    const currentRoomHeader = document.getElementById('current-room');
    const usernameInput = document.getElementById('username-input');
    const logoutButton = document.getElementById('logout-button');
    const leaveChatButton = document.getElementById('leave-chat-button');
    const toggleSwitch = document.getElementById('toggle-switch');

    // Private keys
    const rsaPrivateKey = localStorage.getItem('rsaPrivateKey');
    const dsaPrivateKey = localStorage.getItem('dsaPrivateKey');
    const rsaPublicKey = localStorage.getItem('rsaPublicKey');
    const dsaPublicKey = localStorage.getItem('dsaPublicKey');

    // Global variables
    let current_room = null;
    let current_user_id = null;
    let chat_rooms = []; // List of chat rooms that the user is in
    let messages = []; // List of messages in the current chat room
    let participants = []; // List of participants in the current chat room
    let session_key = null; // Decrypted session key for the current chat room (AES)
    let signatureType = "RSA"; // Default signature algorithm

    // Run once
    function runOnce() {
        socket.emit('query_user_chat_rooms');
        socket.emit('query_user_id');
    }
    
   // Join a room
   window.joinRoom = function (room) {
    // Leave the current room, if any
    if (current_room) {
        socket.emit('leave_room', { 'room_id': current_room.id });
    }
    // Join the new room
    current_room = room;
    socket.emit('join_room', { 'room_id': current_room.id });
    socket.emit('query_chat_room', { 'room_id': current_room.id });
    currentRoomHeader.textContent = `Current Room: ${current_room.name}`;
    };

    // Create a new room
    window.createNewChatSession = function () {
        const room_name = prompt('Enter the name of the new room:');
        socket.emit('create_chat_room', {'chat_name': room_name});
        console.log("Room: " + room_name + " created");
    }
    
    // Update the chat room list
    function updateChatRoomsList(chat_rooms) {
        function addChatRoom(room) {
            const li = document.createElement('li');
            const button = document.createElement('button');
            button.textContent = room.name;
            button.onclick = () => joinRoom(room);
            li.appendChild(button);
            chatRoomsList.appendChild(li);
        }

        // Clear the current chat room list
        chatRoomsList.innerHTML = '';

        // Add each room to the list
        chat_rooms.forEach(room => addChatRoom(room));
    }

    // Update the chat room user list
    function updateUserList(new_users) {
        function addUser(user) {
            const li = document.createElement('li');
            li.textContent = user.username;
            if (user.is_online) {
                li.textContent += ' (Online)';
            } else {
                li.textContent += ' (Offline)';
            }
            userList.appendChild(li);
        }

        // Clear the current user list
        userList.innerHTML = '';

        // Add each user from the new list
        new_users.forEach(user => addUser(user));
    }

    // Update the messages list
    function updateMessagesList(messages) {
        function addMessage(message, session_key) {
            // Decrypt the message content using the session key
            decryptMessage(message.content, session_key).then(decryptedContent => {
                // Verify the sender's signature either RSA or DSA
                verifySignature(signatureType, decryptedContent, message.signatures, {"RSA": rsaPublicKey, "DSA": dsaPublicKey}).then(isValid => {
                    if (!isValid) {
                        console.error('Invalid signature');
                        return;
                    }
                    const li = document.createElement('li');
                    const username = participants.find(user => user.id === message.sender_id).username;
                    li.textContent = `${message.created_at} ${username}: ${decryptedContent}`;
                    messagesList.appendChild(li);
                    }).catch(error => {
                        console.error('Error verifying signature:', error);
                    });
            });
        }

        // Clear the current messages list
        messagesList.innerHTML = '';

        messages.forEach(message => addMessage(message, session_key));
    }

    // Message input event listener
        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                const message = messageInput.value;
                e.preventDefault();
                if (current_room && message) {
                    // Emit the message event
                    signMessageRSA(message, rsaPrivateKey).then(rsa_signature => {
                    signMessageDSA(message, dsaPrivateKey).then(dsa_signature => {
                    encryptMessage(message, session_key).then(enc_msg => {
                        socket.emit('send_message_to_room', {'user_id': current_user_id, 'message': enc_msg, 'room_id': current_room.id, 'rsa_signature': rsa_signature, 'dsa_signature': dsa_signature});
                        console.log("Message: " + message + " sent to room: " + current_room.name);
                        console.log("Encrypted message: " + enc_msg);
                        messageInput.value = '';  // Clear the message input
                    }).catch(error => {
                        console.error('Error encrypting message:', error);
                    });
                }).catch(error => {
                    console.error('Error signing message with DSA:', error);
                });
                }).catch(error => {
                    console.error('Error signing message with RSA:', error);
                });
            }
        };
    });

    // Username input event listener
    usernameInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            username = usernameInput.value;
            e.preventDefault();
            // Must be in a room to add users
            if (current_room && username) {
                // Query user by username
                socket.emit('query_user_by_username', {'username': username});
                socket.on('res_query_user_by_username', data => {
                    user = { 'id': data.user_id, 'username': username };
                    if (user.id === -1) {
                        alert('User not found');
                        return;
                    }
                    socket.emit('add_user_to_chat', {'user_id': user.id, 'room_id': current_room.id});
                    console.log("User: " + username + " added to room: " + current_room.name);
                    usernameInput.value = '';  // Clear the username input
                });
            }
        }
    });

    // Logout button event listener
    logoutButton.onclick = () => {
        fetch('/api/logout', {
            method: 'POST'
        }).then(response => {
            if (response.ok) {
                window.location.href = '/';
            } else {
                alert('Logout failed', response);
            }
        })
    }

    // Leave chat button event listener
    leaveChatButton.onclick = () => {
        if (current_room) {
            socket.emit('remove_user_from_chat', { 'room_id': current_room.id, 'user_id': current_user_id });
            current_room = null;
            currentRoomHeader.textContent = 'Current Room: None';
            messagesList.innerHTML = '';
            userList.innerHTML = '';
            console.log('Left the chat room');
            socket.emit('query_user_chat_rooms');
        }
    };

    // Toggle switch event listener for RSA/DSA digital signature
    toggleSwitch.addEventListener('change', (event) => {
        if (event.target.checked) {
            // DSA digital signature
            signatureType = "DSA";
            console.log('Switched to DSA digital signature');
        } else {
            // RSA digital signature
            signatureType = "RSA";
            console.log('Switched to RSA digital signature');
        }
        // Requery the current chat room
        socket.emit('query_chat_room', { 'room_id': current_room.id });
    });

    // Socket.IO events
    socket.on('res_query_user_chat_rooms', data => {
        chat_rooms = data.chat_rooms;

        // Update the chat room list
        updateChatRoomsList(chat_rooms);
    });

    socket.on('res_query_chat_room', data => {
        current_room = { 'id': data.room_id, 'name': data.room_name };
        participants = data.participants;
        messages = data.messages;
        const encrypted_session_key = data.user_encrypted_key;

        decryptSessionKey(encrypted_session_key, rsaPrivateKey).then(decrypted_session_key => {
            session_key = decrypted_session_key,

            //console.log('chat room query results: ' + current_room.name + ' ' + participants + ' ' + messages + ' ' + encrypted_session_key);
        
            // Update the user list
            updateUserList(participants),

            // Update the messages list
            updateMessagesList(messages)
        });
    });

    // Any time the state of the chat room changes, requery the room info
    socket.on('requery_room', data => {
        if (!current_room) {
            console.log('No current room to requery');
            return;
        }
        socket.emit('query_chat_room', {'room_id': current_room.id});
    });

    socket.on('chat_created', data => {
        socket.emit('query_user_chat_rooms');
    });

    socket.on('res_query_user_id', data => {
        current_user_id = data.user_id;
    });

    runOnce();
});
