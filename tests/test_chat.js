const { JSDOM } = require('jsdom');
const fs = require('fs');
const path = require('path');

const html = fs.readFileSync(path.resolve(__dirname, '../templates/chat.html'), 'utf8');
let dom;
let document;

describe('Chat Interface', () => {
    beforeEach(() => {
        dom = new JSDOM(html, { runScripts: 'dangerously' });
        document = dom.window.document;
    });

    test('should display chat rooms', () => {
        const chatRoomsList = document.getElementById('chat-rooms');
        expect(chatRoomsList).not.toBeNull();
    });

    test('should display messages', () => {
        const messagesList = document.getElementById('message-list');
        expect(messagesList).not.toBeNull();
    });

    test('should display user list', () => {
        const userList = document.getElementById('user-list');
        expect(userList).not.toBeNull();
    });

    test('should have a logout button', () => {
        const logoutButton = document.getElementById('logout-button');
        expect(logoutButton).not.toBeNull();
    });

    test('should have a leave chat button', () => {
        const leaveChatButton = document.getElementById('leave-chat-button');
        expect(leaveChatButton).not.toBeNull();
    });

    test('should have a toggle switch for RSA/DSA', () => {
        const toggleSwitch = document.getElementById('toggle-switch');
        expect(toggleSwitch).not.toBeNull();
    });
});