document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('register-form');
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const username = form.username.value;
        const password = form.password.value;

        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        fetch('/api/register', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                window.location.href = '/login';
            } else {
                alert('Registration failed');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Registration failed');
        });
    });
});