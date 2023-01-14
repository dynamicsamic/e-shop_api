from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from ninja.testing import TestClient

from .api import router, token_create

User = get_user_model()


class AuthTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = TestClient(router)
        cls.urls = {"token": "/token"}
        cls.user_credentials = {
            "username": "new_user",
            "password": "valid_password",
        }
        cls.user = User.objects.create_user(**cls.user_credentials)

    def test_token_uses_right_view_function(self):
        path = self.urls.get("token")
        path_operations = router.path_operations.get(path).operations[0]
        view = path_operations.view_func
        self.assertIs(view, token_create)

    def test_token_with_empty_credentials_returns_422_status_code(self):
        payload = {}
        resp = self.guest_client.post(self.urls.get("token"), json=payload)
        self.assertEqual(resp.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

    def test_token_with_missing_password_returns_422_status_code(self):
        payload = {"username": "user"}
        resp = self.guest_client.post(self.urls.get("token"), json=payload)
        self.assertEqual(resp.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

    def test_token_with_missing_username_returns_422_status_code(self):
        payload = {"password": "psswrd"}
        resp = self.guest_client.post(self.urls.get("token"), json=payload)
        self.assertEqual(resp.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

    def test_token_with_null_user_returns_404_status_code(self):
        payload = {"username": "user", "password": "psswrd"}
        resp = self.guest_client.post(self.urls.get("token"), json=payload)
        self.assertEqual(resp.status_code, HTTPStatus.NOT_FOUND)

    def test_token_with_wrong_password_returns_401_status_code(self):
        payload = {"username": "new_user", "password": "wrong!"}
        resp = self.guest_client.post(self.urls.get("token"), json=payload)
        self.assertEqual(resp.status_code, HTTPStatus.UNAUTHORIZED)

    def test_token_with_valid_credentials_returns_200_status_code(self):
        payload = {
            "username": self.user_credentials.get("username"),
            "password": self.user_credentials.get("password"),
        }
        resp = self.guest_client.post(self.urls.get("token"), json=payload)
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_token_with_valid_credentials_returns_jwt_token(self):
        payload = {
            "username": self.user_credentials.get("username"),
            "password": self.user_credentials.get("password"),
        }
        resp = self.guest_client.post(self.urls.get("token"), json=payload)
        self.assertIn("access_token", resp.json())

    def test_jwt_token_valid(self):
        import datetime as dt

        from x_auth.authentication import BasicAuthBearer

        payload = {
            "username": self.user_credentials.get("username"),
            "password": self.user_credentials.get("password"),
        }
        resp = self.guest_client.post(self.urls.get("token"), json=payload)
        token = resp.json().get("access_token")
        decoded = BasicAuthBearer()._decode(token)
        now_ts = dt.datetime.timestamp(dt.datetime.now())
        self.assertEqual(decoded.get("user_id"), self.user.id)
        self.assertGreater(decoded.get("exp_time"), now_ts)
