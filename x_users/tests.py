import json
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse_lazy
from ninja.testing import TestClient

from tests.factories import UserFactory

from .api import router

USER_NUM = 10

User = get_user_model()


class CreateUsersMixin:
    @classmethod
    def setUpClass(cls):
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

    def test_foo(self):
        resp = self.client.get("/")
        print(resp.json())

    def test_user_create_view_valid_data(self):
        url = reverse_lazy(self.api_url_prefix + "user_create")
        valid_data = {
            "username": "user001",
            "email": "user000dffdfd@hello.py",
            "password": "hello",
        }
        resp = self.client.post(path="create", json=valid_data)

        print(resp.json())
        # print(resp.items())
        print(resp.status_code)
        # valid_data = {
        #    "username": "user000",
        #    "email": "user000@hello.py",
        #    "password": "hello",
        # }
        # resp = self.client.post(path=url, data={"username": "sammi"})
        # print(resp.status_code)
        # print(resp.json())
        # print(resp.request)
