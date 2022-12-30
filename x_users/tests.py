import json
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse_lazy
from ninja.testing import TestClient

from customers.models import Customer
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
            "user_detail": "/{}/",
            "user_update": "/{}/update",
            "user_delete": "/{}/delete",
            "user_create": "/create",
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

    def test_user_detail_with_valid_id_returns_expected_output(self):
        user = User.objects.first()
        url = self.urls.get("user_detail").format(user.id)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, HTTPStatus.OK)

        data = resp.json()
        self.assertTrue(UserOut(**data))
        self.assertTrue(data.get("username"), user.get_username())
        self.assertTrue(data.get("email"), user.email)
        self.assertTrue(data.get("first_name"), user.first_name)
        self.assertTrue(data.get("last_name"), user.last_name)

    def test_user_detail_with_invalid_id_returns_404_status_code(self):
        invalid_id = -10
        url = self.urls.get("user_detail").format(invalid_id)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, HTTPStatus.NOT_FOUND)

    def test_user_detail_with_wrong_format_id_returns_422_status_code(self):
        invalid_id = "invalid"
        url = self.urls.get("user_detail").format(invalid_id)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

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
        self.assertEqual(User.objects.count(), user_num + 1)
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
            self.fail("New user was not created")

    def test_user_create_can_create_customer(self):
        user_num = User.objects.count()
        customer_count = Customer.objects.count()
        valid_data = {
            "username": "user001",
            "email": "user001d@hello.py",
            "password": "hello",
            "create_customer": True,
        }
        resp = self.client.post(path=self.urls["user_create"], json=valid_data)
        result = resp.json()
        self.assertTrue(resp.status_code, HTTPStatus.CREATED)
        self.assertEqual(User.objects.count(), user_num + 1)

        self.assertEqual(Customer.objects.count(), customer_count + 1)
        customer_exists = Customer.objects.filter(
            user__username=valid_data.get("username")
        ).exists()
        self.assertTrue(customer_exists)

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

    def test_user_create_with_not_unique_email_returns_400_status_code(self):
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
        self.assertTrue("error_message" in resp.json())
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

    def test_user_create_with_not_unique_username_returns_400_status_code(
        self,
    ):
        existing_user = self.users[0]
        invalid_data = {
            "username": existing_user.get_username(),
            "email": "user001d@hello.py",
            "password": "hello",
        }
        resp = self.client.post(
            path=self.urls["user_create"], json=invalid_data
        )
        self.assertEqual(resp.status_code, HTTPStatus.BAD_REQUEST)
        self.assertTrue("error_message" in resp.json())
        self.assertFalse(
            User.objects.filter(username=invalid_data.get("email")).exists()
        )

    def test_user_update_with_valid_data_updates_user(self):
        user = self.users[0]
        valid_data = {
            "email": "new_user001@hello.py",
            "first_name": "John",
            "last_name": "Doe",
        }
        url = self.urls.get("user_update").format(user.id)
        resp = self.client.put(url, json=valid_data)
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertTrue(UserOut(**resp.json()))

        updated_user = User.objects.get(id=user.id)
        self.assertEqual(updated_user.email, valid_data.get("email"))
        self.assertEqual(updated_user.first_name, valid_data.get("first_name"))
        self.assertEqual(updated_user.last_name, valid_data.get("last_name"))

    def test_user_update_with_empty_payload_returns_200_status_code(self):
        user = self.users[0]
        empty_payload = {}
        url = self.urls.get("user_update").format(user.id)
        resp = self.client.put(url, json=empty_payload)
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_user_update_with_no_email_field_updates_user(self):
        user = self.users[0]
        valid_data = {
            "first_name": "John",
            "last_name": "Doe",
        }
        url = self.urls.get("user_update").format(user.id)
        resp = self.client.put(url, json=valid_data)
        self.assertEqual(resp.status_code, HTTPStatus.OK)

        updated_user = User.objects.get(id=user.id)
        self.assertEqual(updated_user.first_name, valid_data.get("first_name"))
        self.assertEqual(updated_user.last_name, valid_data.get("last_name"))

    def test_user_update_with_occupied_email_returns_400_status_code(self):
        user = User.objects.first()
        other_user = User.objects.last()
        occupied_email = {
            "email": other_user.email,
        }
        url = self.urls.get("user_update").format(user.id)
        resp = self.client.put(url, json=occupied_email)
        self.assertEqual(resp.status_code, HTTPStatus.BAD_REQUEST)
        self.assertTrue("error_message" in resp.json())
        self.assertTrue("email" in resp.json().get("error_message"))

    def test_user_delete_removes_user_from_db(self):
        user = self.users[0]
        url = self.urls.get("user_delete").format(user.id)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        deleted_user = User.objects.filter(id=user.id).exists()
        self.assertFalse(deleted_user)
