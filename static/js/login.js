// Create and store RSA and DSA key pairs in localStorage

document.addEventListener('DOMContentLoaded', async () => {
    const dsaKeyPair = await generateDSAKeyPair();
    const rsaKeyPair = await generateRSAKeyPair();

    localStorage.setItem('dsaPrivateKey', dsaKeyPair.privateKey);
    localStorage.setItem('dsaPublicKey', dsaKeyPair.publicKey);

    localStorage.setItem('rsaPrivateKey', rsaKeyPair.privateKey);
    localStorage.setItem('rsaPublicKey', rsaKeyPair.publicKey);  

    const form = document.getElementById('login-form');
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const username = form.username.value;
        const password = form.password.value;
        const dsaPublicKey = localStorage.getItem('dsaPublicKey');
        const rsaPublicKey = localStorage.getItem('rsaPublicKey');

        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        formData.append('dsaPublicKey', dsaPublicKey);
        formData.append('rsaPublicKey', rsaPublicKey);

        fetch('/api/login', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                window.location.href = '/chat';
            } else {
                alert('Login failed');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Login failed');
        });
    });
});