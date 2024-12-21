import unittest
from flask import session
from app import app, db
from database import db_create_account, db_check_account, db_update_public_key

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.drop_all()

    def test_register(self):
        response = self.app.post('/api/register', data=dict(
            username='testuser',
            password='testpassword'
        ))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registration successful', response.data)

    def test_login(self):
        with app.app_context():
            db_create_account('testuser', 'hashedpassword', '', '')
        response = self.app.post('/api/login', data=dict(
            username='testuser',
            password='testpassword',
            rsaPublicKey='test_rsa_key',
            dsaPublicKey='test_dsa_key'
        ))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login successful', response.data)

    def test_logout(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1
            response = c.post('/api/logout')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Logout Successful', response.data)

if __name__ == '__main__':
    unittest.main()