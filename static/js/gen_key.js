// Purpose: Generate RSA and DSA key pairs using SubtleCrypto's generateKey method
// Documentation: https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/generateKey

// Generate RSA key pair and return obj with public and private keys
// Public key is in SPKI format and private key is in PKCS#8 format
async function generateRSAKeyPair() {
    const keyPair = await window.crypto.subtle.generateKey(
        {
            name: "RSA-OAEP",
            modulusLength: 4096,
            publicExponent: new Uint8Array([1, 0, 1]),
            hash: "SHA-512"
        },
        true,
        ["encrypt", "decrypt"]
    );

    const publicKey = await window.crypto.subtle.exportKey("spki", keyPair.publicKey);
    const privateKey = await window.crypto.subtle.exportKey("pkcs8", keyPair.privateKey);

    console.log("RSA Public Key:", arrayBufferToBase64(publicKey));
    console.log("RSA Private Key:", arrayBufferToBase64(privateKey));

    return {
        publicKey: publicKey,
        privateKey: privateKey
    };
}

// Generate DSA key pair and return obj with public and private keys
// Public key is in SPKI format and private key is in PKCS#8 format
async function generateDSAKeyPair() {
    const keyPair = await window.crypto.subtle.generateKey(
        {
            name: "DSA",
            modulusLength: 2048,
            hash: "SHA-256",
            divisorLength: 256
        },
        true,
        ["sign", "verify"]
    );

    const publicKey = await window.crypto.subtle.exportKey("spki", keyPair.publicKey);
    const privateKey = await window.crypto.subtle.exportKey("pkcs8", keyPair.privateKey);

    console.log("DSA Public Key:", arrayBufferToBase64(publicKey));
    console.log("DSA Private Key:", arrayBufferToBase64(privateKey));

    return {
        publicKey: publicKey,
        privateKey: privateKey
    };
}

function arrayBufferToBase64(buffer) {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);
}

// Generate the keys
generateRSAKeyPair();
generateDSAKeyPair();