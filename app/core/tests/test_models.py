from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email_success(self):

        """tests creating new user with email is successful"""
        email = "test@gmail.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
         email=email,
         password=password,
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Tests if user email is created with all small letters"""
        email = "test@GMAIL.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email.lower())

    def test_new_user_valid_email(self):
        """Test if email is valid , raise value error if not"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "12345")

    def test_create_new_superusr(self):
        """Test creating suprer user"""
        email = "test@gmail.com"
        password = "test123"

        user = get_user_model().objects.create_super_user(
            email,
            password
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
