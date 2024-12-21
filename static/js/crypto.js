// Using Web Crypto API to generate RSA and DSA key pairs, encrypt and decrypt messages, and sign and verify signatures
async function generateRSAKeyPair() {
    try {
        const keyPair = await window.crypto.subtle.generateKey(
            {
                name: "RSA-OAEP",
                modulusLength: 2048,
                publicExponent: new Uint8Array([1, 0, 1]),
                hash: "SHA-256"
            },
            true,
            ["encrypt", "decrypt"]
        );

        const publicKey = await window.crypto.subtle.exportKey("spki", keyPair.publicKey);
        const privateKey = await window.crypto.subtle.exportKey("pkcs8", keyPair.privateKey);

        return {
            publicKey: arrayBufferToBase64(publicKey),
            privateKey: arrayBufferToBase64(privateKey)
        };
    } catch (error) {
        console.error('Error generating RSA key pair:', error);
        throw error;
    }
}

// Generate DSA key pair and return obj with public and private keys
// Public key is in SPKI format and private key is in PKCS#8 format
async function generateDSAKeyPair() {
    try {
        const keyPair = await window.crypto.subtle.generateKey(
            {
                name: "ECDSA",
                namedCurve: "P-384"
            },
            true,
            ["sign", "verify"]
        );

        const publicKey = await window.crypto.subtle.exportKey("spki", keyPair.publicKey);
        const privateKey = await window.crypto.subtle.exportKey("pkcs8", keyPair.privateKey);

        return {
            publicKey: arrayBufferToBase64(publicKey),
            privateKey: arrayBufferToBase64(privateKey)
        };
    } catch (error) {
        console.error('Error generating DSA key pair:', error);
        throw error;
    }
}

// Convert an ArrayBuffer to a base64 string
function arrayBufferToBase64(buffer) {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);
}

// Convert a base64 string to an ArrayBuffer
function base64ToArrayBuffer(base64) {
    const binary_string = window.atob(base64);
    const bytes = new Uint8Array(binary_string.length);
    for (let i = 0; i < binary_string.length; i++) {
        bytes[i] = binary_string.charCodeAt(i);
    }
    return bytes.buffer;
}

// Decrypt the session key using RSA private key
// encrypted_session_key is base64 encoded string
// rsaPrivateKey is base64 encoded string
async function decryptSessionKey(encrypted_session_key, rsaPrivateKey) {
    try {
        console.log('Encrypted Session Key: ' + encrypted_session_key);
        const privateKey = await window.crypto.subtle.importKey(
            "pkcs8",
            base64ToArrayBuffer(rsaPrivateKey),
            {
                name: "RSA-OAEP",
                hash: "SHA-256"
            },
            true,
            ["decrypt"]
        );

        const session_key = await window.crypto.subtle.decrypt(
            {
                name: "RSA-OAEP"
            },
            privateKey,
            base64ToArrayBuffer(encrypted_session_key)
        );

        console.log('Session key decrypted:', arrayBufferToBase64(session_key));
        return session_key;
    } catch (error) {
        console.error('Error decrypting session key:', error);
        throw error;
    }
}

// Decrypt a message with AES
async function decryptMessage(encryptedMessageBase64, session_key) {
    try {
        if (!session_key) {
            console.error('Session key not found');
            throw new Error('Session key not found');
        }

        // Decode the Base64-encoded encrypted message into a Uint8Array
        const encryptedMessage = base64ToArrayBuffer(encryptedMessageBase64);
        const iv = encryptedMessage.slice(0, 12); // Extract the IV (first 12 bytes)
        const ciphertext = encryptedMessage.slice(12); // Extract the ciphertext (remaining bytes)

        // Import the AES key
        const key = await window.crypto.subtle.importKey(
            "raw",
            session_key,
            {
                name: "AES-GCM"
            },
            false,
            ["decrypt"]
        );

        // Decrypt the ciphertext
        const decryptedArrayBuffer = await window.crypto.subtle.decrypt(
            {
                name: "AES-GCM",
                iv: iv,
                tagLength: 128
            },
            key,
            ciphertext
        );

        // Convert the decrypted data back to a string
        const decryptedMessage = new TextDecoder().decode(decryptedArrayBuffer);
        return decryptedMessage;
    } catch (error) {
        console.error('Error decrypting message:', error);
        throw error;
    }
}

// Encrypt a message with AES
// Message is string, session_key is ArrayBuffer
async function encryptMessage(message, session_key) {
    try {
        if (!session_key) {
            console.error('Session key not found');
            throw new Error('Session key not found');
        }
        const iv = window.crypto.getRandomValues(new Uint8Array(12));
        const encodedMessage = new TextEncoder().encode(message);

        const key = await window.crypto.subtle.importKey(
            "raw",
            session_key,
            {
                name: "AES-GCM"
            },
            false,
            ["encrypt"]
        );
        const ciphertext = await window.crypto.subtle.encrypt(
            {
                name: "AES-GCM",
                iv: iv,
                tagLength: 128
            },
            key,
            encodedMessage
        );

        const encryptedMessage = new Uint8Array(ciphertext.byteLength + iv.byteLength);
        encryptedMessage.set(new Uint8Array(iv), 0);
        encryptedMessage.set(new Uint8Array(ciphertext), iv.byteLength);

        return arrayBufferToBase64(encryptedMessage);
    } catch (error) {
        console.error('Error encrypting message:', error);
        throw error;
    }
}

// Sign a message with DSA
async function signMessageDSA(message, dsaPrivateKey) {
    try {
        const privateKey = await window.crypto.subtle.importKey(
            "pkcs8",
            base64ToArrayBuffer(dsaPrivateKey),
            {
                name: "ECDSA",
                namedCurve: "P-384"
            },
            true,
            ["sign"]
        );

        const encodedMessage = new TextEncoder().encode(message);
        const signature = await window.crypto.subtle.sign(
            {
                name: "ECDSA",
                hash: {name: "SHA-384"}
            },
            privateKey,
            encodedMessage
        );

        return arrayBufferToBase64(signature);
    } catch (error) {
        console.error('Error signing message:', error);
        throw error;
    }
}

// Sign a message with RSA
async function signMessageRSA(message, rsaPrivateKey) {
    try {
        const privateKey = await window.crypto.subtle.importKey(
            "pkcs8",
            base64ToArrayBuffer(rsaPrivateKey),
            {
                name: "RSA-PSS",
                hash: "SHA-256"
            },
            true,
            ["sign"]
        );

        const encodedMessage = new TextEncoder().encode(message);
        const signature = await window.crypto.subtle.sign(
            {
                name: "RSA-PSS",
                saltLength: 32
            },
            privateKey,
            encodedMessage
        );

        return arrayBufferToBase64(signature);
    } catch (error) {
        console.error('Error signing message:', error);
        throw error;
    }
}

// Verify a DSA signature
async function verifySignatureDSA(message, signature, publicKey) {
    try {
        const key = await window.crypto.subtle.importKey(
            "spki",
            base64ToArrayBuffer(publicKey),
            {
                name: "ECDSA",
                namedCurve: "P-384"
            },
            true,
            ["verify"]
        );

        const encodedMessage = new TextEncoder().encode(message);
        const signatureBuffer = base64ToArrayBuffer(signature);
        const result = await window.crypto.subtle.verify(
            {
                name: "ECDSA",
                hash: {name: "SHA-384"}
            },
            key,
            signatureBuffer,
            encodedMessage
        );

        console.log('DSA signature verified: ', result);
        return result;
    } catch (error) {
        console.error('Error verifying signature:', error);
        throw error;
    }
}

// Verify an RSA signature
async function verifySignatureRSA(message, signature, publicKey) {
    try {
        const key = await window.crypto.subtle.importKey(
            "spki",
            base64ToArrayBuffer(publicKey),
            {
                name: "RSA-PSS",
                hash: "SHA-256"
            },
            true,
            ["verify"]
        );

        const encodedMessage = new TextEncoder().encode(message);
        const signatureBuffer = base64ToArrayBuffer(signature);
        const result = await window.crypto.subtle.verify(
            {
                name: "RSA-PSS",
                saltLength: 32
            },
            key,
            signatureBuffer,
            encodedMessage
        );
        console.log('RSA signature verified: ', result);
        return result;
    } catch (error) {
        console.error('Error verifying signature:', error);
        throw error;
    }
}

// Verify a signature using either RSA or DSA
async function verifySignature(signatureType, message, signature, publicKey) {
    if (signatureType === 'RSA') {
        return await verifySignatureRSA(message, signature.RSA, publicKey.RSA);
    } else if (signatureType === 'DSA') {
        return await verifySignatureDSA(message, signature.DSA, publicKey.DSA);
    } else {
        throw new Error('Invalid signature type');
    }
}