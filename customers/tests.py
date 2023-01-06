from http import HTTPStatus

from django.test import TestCase
from ninja.testing import TestClient

from tests.factories import CustomerFactory
from x_users.tests import USER_NUM, CreateUsersMixin

from .api import customer_detail, customer_list, router
from .models import Customer
from .schemas import CustomerOut


class CreateCustomersMixin(CreateUsersMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customers = CustomerFactory.create_batch(USER_NUM)
        cls.ninja_client = TestClient(router)
        cls.urls = {
            "customer_list": "/",
            "customer_detail": "/{id}/",
            "customer_update": "/{}/update",
            "customer_delete": "/{}/delete",
            "customer_create": "/create",
        }


class CustomerApiTestCase(CreateCustomersMixin, TestCase):

    ### CUSTOMER LIST SECTION ###
    def test_customer_list_uses_right_view_func(self):
        path = self.urls.get("customer_list")
        path_operations = router.path_operations.get(path).operations[0]
        view = path_operations.view_func
        self.assertIs(view, customer_list)

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

        # In a response Ninja's Schema automatically replaces submodel attributes
        # like `user.username` with a given attribute name like `username`.
        # But to validate the output result we need to bring those dotted
        # attributes to their initial place.
        # Need to work this out later.
        for item in data:
            item["user.username"] = item.pop("username")
            item["user.email"] = item.pop("email")
        self.assertTrue(all(schema(**item) for item in data))

    def test_customer_list_returns_empty_list_when_no_customer_exists(self):
        Customer.objects.all().delete()
        resp = self.ninja_client.get(self.urls.get("customer_list"))
        self.assertEqual(resp.json(), [])

    ### CUSTOMER DETAIL SECTION ###
    def test_customer_detal_uses_right_view_func(self):
        path = self.urls.get("customer_detail")
        path_operations = router.path_operations.get(path).operations[0]
        view = path_operations.view_func
        self.assertIs(view, customer_detail)

    def test_customer_detail_returns_200_status_code_with_valid_id(self):
        customer = self.customers[0]
        resp = self.ninja_client.get(
            self.urls.get("customer_detail").format(id=customer.id)
        )
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_customer_detail_returns_404_status_code_with_invalid_id(self):
        invalid_id = -1
        resp = self.ninja_client.get(
            self.urls.get("customer_detail").format(id=invalid_id)
        )
        self.assertEqual(resp.status_code, HTTPStatus.NOT_FOUND)

    def test_customer_detail_returns_422_status_code_with_wrong_type_id(self):
        wrong_type_id = "wrong"
        resp = self.ninja_client.get(
            self.urls.get("customer_detail").format(id=wrong_type_id)
        )
        self.assertEqual(resp.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

    def test_customer_detail_returns_non_sequence(self):
        from typing import Sequence

        customer = self.customers[0]
        resp = self.ninja_client.get(
            self.urls.get("customer_detail").format(id=customer.id)
        )
        self.assertNotIsInstance(resp.json(), Sequence)

    def test_customer_detail_response_contains_keys_from_schema(self):
        schema = CustomerOut.schema(by_alias=False)
        expected_keys = schema.get("properties").keys()
        customer = self.customers[0]
        resp = self.ninja_client.get(
            self.urls.get("customer_detail").format(id=customer.id)
        )
        self.assertEqual(resp.json().keys(), expected_keys)

    def test_customer_detail_response_dict_follow_specific_schema(self):
        customer = self.customers[0]
        resp = self.ninja_client.get(
            self.urls.get("customer_detail").format(id=customer.id)
        )
        resp_data = resp.json().copy()
        resp_data["user.username"] = resp_data.pop("username")
        resp_data["user.email"] = resp_data.pop("email")
        self.assertTrue(CustomerOut(**resp_data))
