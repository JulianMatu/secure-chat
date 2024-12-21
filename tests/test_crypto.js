const { generateRSAKeyPair, generateDSAKeyPair, encryptMessage, decryptMessage, signMessageRSA, signMessageDSA, verifySignature } = require('../static/js/crypto');

describe('Crypto Functions', () => {
    let rsaKeyPair, dsaKeyPair, message, encryptedMessage, rsaSignature, dsaSignature;

    beforeAll(async () => {
        rsaKeyPair = await generateRSAKeyPair();
        dsaKeyPair = await generateDSAKeyPair();
        message = 'Hello, world!';
        encryptedMessage = await encryptMessage(message, rsaKeyPair.publicKey);
        rsaSignature = await signMessageRSA(message, rsaKeyPair.privateKey);
        dsaSignature = await signMessageDSA(message, dsaKeyPair.privateKey);
    });

    test('should encrypt and decrypt message', async () => {
        const decryptedMessage = await decryptMessage(encryptedMessage, rsaKeyPair.privateKey);
        expect(decryptedMessage).toBe(message);
    });

    test('should sign and verify RSA signature', async () => {
        const isValid = await verifySignature('RSA', message, { RSA: rsaSignature }, { RSA: rsaKeyPair.publicKey });
        expect(isValid).toBe(true);
    });

    test('should sign and verify DSA signature', async () => {
        const isValid = await verifySignature('DSA', message, { DSA: dsaSignature }, { DSA: dsaKeyPair.publicKey });
        expect(isValid).toBe(true);
    });
});