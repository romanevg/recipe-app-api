from django.test import TestCase
from django.contrib.auth import get_user_model

# reverse is needed for generating API URL
from django.urls import reverse

# this test is a test client that we can use to make requests
# to our API and then check what the response is
from rest_framework.test import APIClient
from rest_framework import status

# В функции reverse(): 'user'- пространство имен, 'create' - именованный URL.
# Namespaces can also be nested. The named URL 'sports:polls:index' would look
# for a pattern named 'index' in the namespace 'polls' that is itself defined
# within the top-level namespace 'sports'.
CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


# Делать приватные и публичные классы для тестирования - личное предпочтение.
# Например публичные тестируют запросы неаутентифицированного пользователя,
# а приватные - аутентифицированного, например, изменение пароля
# или модификация пользователя.
class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """
        Test creating user with valid payload is successful
        (payload - is object that we pass to the API when make the request).
        """
        payload = {
            'email': 'test@django.com',
            'password': 'test123',
            'name': 'Django Vue'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        # проверяем правильность пароля
        self.assertTrue(user.check_password(payload['password']))
        # проверяем, чтобы пароль не возвращался в запросе (для безопасности)
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating a user that already exists fails."""
        payload = {'email': 'test@django.com', 'password': 'test123'}
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 characters"""
        payload = {'email': 'test@django.com', 'password': 'vue'}
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is crated for the user"""
        payload = {'email': 'test@django.com', 'password': 'test123'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given."""
        create_user(email='test@django.com', password='test123')
        payload = {'email': 'test@django.com', 'password': 'wrong'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """
        Test that token is not created if user doesn't exist.
        В этом тесте мы сделаем запрос без создания пользователя.
        Т.к. для каждого теста база данных создается с нуля, не стоит
        беспокоиться о том,что пользователь был создан в предыдущем тесте.
        """
        payload = {'email': 'test@django.com', 'password': 'test123'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required."""
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
