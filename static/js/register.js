// Create and store RSA and DSA key pairs in localStorage

document.addEventListener('DOMContentLoaded', () => {
    const dsaKeyPair = generateDSAKeyPair();
    const rsaKeyPair = generateRSAKeyPair();

    localStorage.setItem('dsaPrivateKey', dsaKeyPair.privateKey);
    localStorage.setItem('dsaPublicKey', dsaKeyPair.publicKey);

    localStorage.setItem('rsaPrivateKey', rsaKeyPair.privateKey);
    localStorage.setItem('rsaPublicKey', rsaKeyPair.publicKey);

    const form = document.getElementById('register-form');
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const username = form.username.value;
        const password = form.password.value;
        const dsaPublicKey = localStorage.getItem('dsaPublicKey');
        const rsaPublicKey = localStorage.getItem('rsaPublicKey');

        const response = fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                password: password,
                dsaPublicKey: dsaPublicKey,
                rsaPublicKey: rsaPublicKey
            })
        });

        if (response.ok) {
            window.location.href = '/login';
        } else {
            const error = response.json();
            alert('Registration failed: ' + error.message);
        }
    });
});