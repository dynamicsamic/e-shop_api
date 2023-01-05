from http import HTTPStatus

from django.test import TestCase
from ninja.testing import TestClient

from tests.factories import CustomerFactory
from x_users.tests import USER_NUM, CreateUsersMixin

from .api import router
from .schemas import CustomerOut


class CreateCustomersMixin(CreateUsersMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customers = CustomerFactory.create_batch(USER_NUM)
        cls.ninja_client = TestClient(router)
        cls.urls = {
            "customer_list": "/",
            "user_detail": "/{}/",
            "user_update": "/{}/update",
            "user_delete": "/{}/delete",
            "user_create": "/create",
        }


from django.urls import resolve, reverse


class CustomerApiTestCase(CreateCustomersMixin, TestCase):
    def test_customer_list_returns_200_status_code(self):
        resp = self.ninja_client.get(self.urls.get("customer_list"))
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_customer_list_returns_all_customers(self):
        resp = self.ninja_client.get(self.urls.get("customer_list"))
        self.assertEqual(len(resp.json()), USER_NUM)

    def test_customer_list_all_response_items_follow_specific_schema(self):
        schema = CustomerOut
        resp = self.ninja_client.get(self.urls.get("customer_list"))

        data = resp.json().copy()
        for item in data:
            item["user.username"] = item.pop("username")
            item["user.email"] = item.pop("email")
        self.assertTrue(all(schema(**item) for item in data))
