from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from ninja.testing import TestClient

from .api import router, signup, token_create

User = get_user_model()


class AuthTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = TestClient(router)
        cls.urls = {"token": "/token", "signup": "/signup"}
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

    ### SIGNUP TESTS
    def test_signup_uses_right_view_func(self):
        path = self.urls.get("signup")
        path_operations = router.path_operations.get(path).operations[0]
        view = path_operations.view_func
        self.assertIs(view, signup)

    def test_signup_with_empty_payload_returns_422_status_code(self):
        payload = {}
        resp = self.guest_client.post(self.urls.get("signup"), json=payload)
        self.assertEqual(resp.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

    def test_signup_with_missing_field_returns_422_status_code(self):
        resp1 = self.guest_client.post(
            self.urls.get("signup"), json={"username": "sammy"}
        )
        resp2 = self.guest_client.post(
            self.urls.get("signup"), json={"email": "sammy@hello.py"}
        )
        resp3 = self.guest_client.post(
            self.urls.get("signup"), json={"password": "valid_pswrd"}
        )
        self.assertEqual(resp1.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertEqual(resp2.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertEqual(resp3.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

    def test_signup_with_existing_credentials_returns_400_status_code(self):
        payload = self.user_credentials.copy()
        payload["email"] = "user@hello.py"
        resp = self.guest_client.post(self.urls.get("signup"), json=payload)
        self.assertEqual(resp.status_code, 400)

    def test_signup_with_valid_payload_returns_200_status_code(self):
        payload = {
            "username": "another_user",
            "password": "another_password",
            "email": "anotheremail@hello.py",
        }
        resp = self.guest_client.post(self.urls.get("signup"), json=payload)
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_signup_with_valid_payload_creates_inactive_user(self):
        initial_user_num = User.objects.count()
        payload = {
            "username": "another_user",
            "password": "another_password",
            "email": "anotheremail@hello.py",
        }
        self.guest_client.post(self.urls.get("signup"), json=payload)
        self.assertEqual(initial_user_num + 1, User.objects.count())

        user = User.objects.get(username=payload["username"])
        self.assertFalse(user.is_active)

    def test_signup_with_valid_payload_creates_user_with_given_fields(self):
        payload = {
            "username": "another_user",
            "password": "another_password",
            "email": "anotheremail@hello.py",
        }
        self.guest_client.post(self.urls.get("signup"), json=payload)
        user = User.objects.get(username=payload["username"])
        self.assertEqual(user.username, payload["username"])
        self.assertEqual(user.email, payload["email"])
        self.assertTrue(user.check_password(payload["password"]))

    def test_signup_with_valid_payload_sends_email(self):
        from django.core import mail

        initial_outbox_num = len(mail.outbox)
        payload = {
            "username": "another_user",
            "password": "another_password",
            "email": "anotheremail@hello.py",
        }
        self.guest_client.post(self.urls.get("signup"), json=payload)
        self.assertEqual(initial_outbox_num + 1, len(mail.outbox))
