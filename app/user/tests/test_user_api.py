from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Tests users api public"""

    def setUp(self):
        self.api_client = APIClient()

    def test_create_valid_user_success(self):
        """Tests create user with valid payload(params) success"""
        payload = {
            'email': "test@gmail.com",
            'password': "password",
            'name': "test"
        }

        res = self.api_client.post(CREATE_USER_URL, payload)
        """201 for created"""
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn("password", res.data)

    def test_user_exists(self):
        """Tests create user already exists"""

        payload = {
            'email': "test@gmail.com",
            'password': "password",
            'name': "test"
        }
        create_user(**payload)
        res = self.api_client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Passsword must be more than 5 chars"""
        payload = {
            'email': "test@gmail.com",
            'password': "pw",
            'name': "test"
        }

        res = self.api_client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertEqual(user_exists, False)

    def test_create_token_for_user(self):
        """Test Create token for user"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'password'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_usertoken_invalid_credentials(self):
        """Test user token not created when invalid token passed"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'password'
        }
        create_user(**payload)
        payload['password'] = '12345'

        res = self.api_client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Tests that token is not created if user does not exists"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'password'
        }

        res = self.api_client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that token is not created if user password is missing"""
        payload = {
            'email': 'test@gmail.com'
        }
        res = self.api_client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_view_profile_when_not_loggedin(self):
        """Test that view profile not allowed when not logged in"""
        res = self.api_client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require Authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@gmail.com',
            password='password',
            name='name',
        )
        self.api_client = APIClient()
        self.api_client.force_authenticate(self.user)

    def test_retrive_profile_success(self):
        """Tests if authenticated user can access his profile"""
        res = self.api_client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """Test if post not allowed for existing user"""
        res = self.api_client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test update user profile for authenticated user"""
        payload = {
            'name': 'Newname',
            'password': 'NewPassword'
        }

        res = self.api_client.patch(ME_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
