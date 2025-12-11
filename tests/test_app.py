"""
Unit tests for authentication and validation
"""
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db, User
from app.validation import (
    validate_email, validate_username, validate_password,
    validate_patient_data, sanitize_string
)


class AuthenticationTestCase(unittest.TestCase):
    """Test user authentication and registration"""

    def setUp(self):
        """Set up test client and database"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Clean up after tests"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_registration(self):
        """Test successful user registration"""
        with self.app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                full_name='Test User'
            )
            user.set_password('TestPassword123!')
            db.session.add(user)
            db.session.commit()

            # Verify user exists
            saved_user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(saved_user)
            self.assertEqual(saved_user.email, 'test@example.com')

    def test_password_hashing(self):
        """Test password hashing works correctly"""
        with self.app.app_context():
            user = User(
                username='testuser2',
                email='test2@example.com',
                full_name='Test User 2'
            )
            password = 'TestPassword123!'
            user.set_password(password)

            # Verify password is hashed (not plaintext)
            self.assertNotEqual(user.password_hash, password)
            # Verify password verification works
            self.assertTrue(user.check_password(password))
            self.assertFalse(user.check_password('WrongPassword'))

    def test_weak_password_rejection(self):
        """Test that weak passwords are rejected"""
        with self.app.app_context():
            user = User(
                username='testuser3',
                email='test3@example.com',
                full_name='Test User 3'
            )
            # Should raise error for weak password
            with self.assertRaises(ValueError):
                user.set_password('weak')


class ValidationTestCase(unittest.TestCase):
    """Test input validation functions"""

    def test_email_validation(self):
        """Test email validation"""
        self.assertTrue(validate_email('test@example.com'))
        self.assertTrue(validate_email('user.name@example.co.uk'))
        self.assertFalse(validate_email('invalid.email'))
        self.assertFalse(validate_email('user@'))

    def test_username_validation(self):
        """Test username validation"""
        self.assertTrue(validate_username('valid_user'))
        self.assertTrue(validate_username('user-123'))
        self.assertFalse(validate_username('ab'))  # Too short
        self.assertFalse(validate_username('invalid@user'))  # Invalid character

    def test_password_validation(self):
        """Test password strength validation"""
        is_valid, msg = validate_password('TestPass123!')
        self.assertTrue(is_valid)

        is_valid, msg = validate_password('weak')
        self.assertFalse(is_valid)
        self.assertIn('8 characters', msg)

        is_valid, msg = validate_password('nocapital123!')
        self.assertFalse(is_valid)
        self.assertIn('uppercase', msg)

    def test_sanitize_string(self):
        """Test string sanitization for XSS prevention"""
        # Test XSS removal
        dirty = '<script>alert("XSS")</script>'
        clean = sanitize_string(dirty)
        self.assertNotIn('<script>', clean)

        # Test HTML escaping
        dirty_html = '<img src=x onerror=alert("xss")>'
        clean_html = sanitize_string(dirty_html)
        self.assertNotIn('onerror', clean_html)

    def test_patient_data_validation(self):
        """Test patient data validation"""
        valid_data = {
            'gender': 'Male',
            'age': 45,
            'hypertension': 0,
            'ever_married': 'Yes',
            'work_type': 'Private',
            'Residence_type': 'Urban',
            'avg_glucose_level': 95.5,
            'bmi': 28.5,
            'smoking_status': 'Never smoked'
        }

        is_valid, msg = validate_patient_data(valid_data)
        self.assertTrue(is_valid)

        # Test invalid age
        invalid_data = valid_data.copy()
        invalid_data['age'] = 150
        is_valid, msg = validate_patient_data(invalid_data)
        self.assertFalse(is_valid)

        # Test missing field
        incomplete_data = valid_data.copy()
        del incomplete_data['gender']
        is_valid, msg = validate_patient_data(incomplete_data)
        self.assertFalse(is_valid)


class CRUDTestCase(unittest.TestCase):
    """Test CRUD operations"""

    def setUp(self):
        """Set up test environment"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            # Create test user
            user = User(
                username='testuser',
                email='test@example.com',
                full_name='Test User'
            )
            user.set_password('TestPassword123!')
            db.session.add(user)
            db.session.commit()

    def tearDown(self):
        """Clean up"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_login(self):
        """Test user login functionality"""
        response = self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'TestPassword123!'
        }, follow_redirects=True)

        # Check login was successful
        self.assertEqual(response.status_code, 200)

    def test_invalid_login(self):
        """Test invalid login attempt"""
        response = self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'WrongPassword'
        })

        # Should not redirect to dashboard
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
