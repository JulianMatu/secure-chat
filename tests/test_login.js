const { JSDOM } = require('jsdom');
const fs = require('fs');
const path = require('path');

const html = fs.readFileSync(path.resolve(__dirname, '../templates/login.html'), 'utf8');
let dom;
let document;

describe('Login Interface', () => {
    beforeEach(() => {
        dom = new JSDOM(html, { runScripts: 'dangerously' });
        document = dom.window.document;
    });

    test('should have a username input', () => {
        const usernameInput = document.getElementById('username');
        expect(usernameInput).not.toBeNull();
    });

    test('should have a password input', () => {
        const passwordInput = document.getElementById('password');
        expect(passwordInput).not.toBeNull();
    });

    test('should have a login button', () => {
        const loginButton = document.querySelector('button[type="submit"]');
        expect(loginButton).not.toBeNull();
    });

    test('should have a registration link', () => {
        const registerLink = document.querySelector('a[href="/register"]');
        expect(registerLink).not.toBeNull();
    });
});