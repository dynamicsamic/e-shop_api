import json
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse_lazy
from ninja.testing import TestClient

from tests.factories import UserFactory

from .api import router
from .schemas import UserOut

USER_NUM = 10

User = get_user_model()


class CreateUsersMixin:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.users = UserFactory.create_batch(USER_NUM)
        for user in cls.users:
            user.set_password(user.password)
            user.save(update_fields=("password",))


class UserModelTestCase(TestCase):
    def setUp(self):
        self.api_url_prefix = "api-1.0.0:"
        self.users = UserFactory.create_batch(USER_NUM)
        for user in self.users:
            user.set_password(user.password)
            user.save(update_fields=("password",))

    def test_user_objects_have_custom_manager(self):
        from x_users.models import CustomUserManager

        self.assertTrue(
            all(
                isinstance(user._meta.model.objects, CustomUserManager)
                for user in self.users
            )
        )

    def test_can_create_customer_along_with_user(self):

        from customers.models import Customer

        valid_data = {
            "username": "user000",
            "email": "user000@hello.py",
            "password": "hello",
            "create_customer": True,
        }
        customer_num_initial = Customer.objects.count()
        User.objects.create_user(**valid_data)
        self.assertEqual(Customer.objects.count(), customer_num_initial + 1)

    def test_user_list_view(self):
        url = reverse_lazy(self.api_url_prefix + "user_list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(len(resp.json()), len(self.users))


class UserApiTestCase(CreateUsersMixin, TestCase):
    def setUp(self):
        self.client = TestClient(router)
        self.urls = {
            "user_list": "/",
            "user_create": "/create",
            "user_detail": "/<id>/",
        }

    #        print(list(router.urls_paths("api-1.0.0")))

    def test_user_list_returns_list_of_all_users(self):
        user_num = User.objects.count()
        resp = self.client.get(self.urls["user_list"])
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(len(resp.json()), user_num)

    def test_user_list_contains_only_specific_schema_items(self):
        resp = self.client.get(self.urls["user_list"])
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertTrue(all(UserOut(**item) for item in resp.json()))

    def test_user_list_returns_empty_list_when_no_users_exist(self):
        User.objects.all().delete()
        resp = self.client.get(self.urls["user_list"])
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(resp.json(), [])

    def test_user_create_with_valid_data_creates_user(self):
        user_num = User.objects.count()
        valid_data = {
            "username": "user001",
            "email": "user001d@hello.py",
            "password": "hello",
        }
        resp = self.client.post(path=self.urls["user_create"], json=valid_data)
        result = resp.json()
        self.assertTrue(resp.status_code, HTTPStatus.CREATED)
        self.assertTrue(User.objects.count(), user_num + 1)
        self.assertTrue(UserOut(**result))

        if new_user := User.objects.filter(
            username=result.get("username")
        ).first():
            self.assertEqual(new_user.get_username(), result.get("username"))
            self.assertEqual(new_user.email, result.get("email"))
            self.assertFalse("password" in result)
            self.assertFalse(new_user.is_active)
            self.assertFalse(new_user.is_superuser)
            self.assertFalse(new_user.is_active)
        else:
            self.fail()

    def test_user_create_with_missing_email_returns_422_status_code(self):
        invalid_data = {
            "username": "user001",
            "password": "hello",
        }
        resp = self.client.post(
            path=self.urls["user_create"], json=invalid_data
        )
        self.assertEqual(resp.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertFalse(
            User.objects.filter(username=invalid_data.get("username")).exists()
        )

    def test_user_create_with_invalid_email_returns_422_status_code(self):
        invalid_data = {
            "username": "user001",
            "email": "invalid_email",
            "password": "hello",
        }
        resp = self.client.post(
            path=self.urls["user_create"], json=invalid_data
        )
        self.assertEqual(resp.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertFalse(
            User.objects.filter(username=invalid_data.get("username")).exists()
        )

    def test_user_create_with_not_unique_email_returns_422_status_code(self):
        existing_user = self.users[0]
        invalid_data = {
            "username": "user001",
            "email": existing_user.email,
            "password": "hello",
        }
        resp = self.client.post(
            path=self.urls["user_create"], json=invalid_data
        )
        self.assertEqual(resp.status_code, HTTPStatus.BAD_REQUEST)
        self.assertFalse(
            User.objects.filter(username=invalid_data.get("username")).exists()
        )

    def test_user_create_with_missing_password_returns_422_status_code(self):
        invalid_data = {
            "username": "user001",
            "email": "user001d@hello.py",
        }
        resp = self.client.post(
            path=self.urls["user_create"], json=invalid_data
        )
        self.assertEqual(resp.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertFalse(
            User.objects.filter(username=invalid_data.get("username")).exists()
        )

    def test_user_create_with_blank_password_returns_422_status_code(self):
        invalid_data = {
            "username": "user001",
            "email": "user001d@hello.py",
            "password": "",
        }
        resp = self.client.post(
            path=self.urls["user_create"], json=invalid_data
        )
        self.assertEqual(resp.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertFalse(
            User.objects.filter(username=invalid_data.get("username")).exists()
        )

    def test_user_create_with_missing_username_returns_422_status_code(self):
        invalid_data = {
            "email": "user001d@hello.py",
            "password": "hello",
        }
        resp = self.client.post(
            path=self.urls["user_create"], json=invalid_data
        )
        self.assertEqual(resp.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertFalse(
            User.objects.filter(username=invalid_data.get("username")).exists()
        )

    def test_user_create_with_too_short_username_returns_422_status_code(self):
        invalid_data = {
            "username": "us",
            "email": "user001d@hello.py",
            "password": "hello",
        }
        resp = self.client.post(
            path=self.urls["user_create"], json=invalid_data
        )
        self.assertEqual(resp.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertFalse(
            User.objects.filter(username=invalid_data.get("username")).exists()
        )
