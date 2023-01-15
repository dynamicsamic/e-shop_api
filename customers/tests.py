from http import HTTPStatus

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from ninja.testing import TestClient

from tests.clients import AuthClient
from tests.factories import CustomerFactory
from x_auth.authentication import get_token
from x_users.tests import USER_NUM, CreateUsersMixin

from .api import (
    customer_create,
    customer_delete,
    customer_detail,
    customer_list,
    customer_update,
    router,
)
from .models import Customer
from .schemas import CustomerOut

User = get_user_model()


class CreateCustomersMixin(CreateUsersMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customers = CustomerFactory.create_batch(USER_NUM)
        cls.admin = User.objects.create_superuser(
            username="admin", password="admin", email="admin@hello.py"
        )
        admin_token = get_token(cls.admin)
        user_token = get_token(cls.customers[0].user)
        cls.guest_client = TestClient(router)
        cls.admin_client = AuthClient(router, admin_token)
        cls.user_client = AuthClient(router, user_token)
        cls.urls = {
            "customer_list": "/",
            "customer_create": "/create",
            "customer_detail": "/{id}/",
            "customer_update": "/{id}/update",
            "customer_delete": "/{id}/delete",
        }


class CustomerApiTestCase(CreateCustomersMixin, TestCase):

    ### CUSTOMER LIST SECTION ###
    def test_list_uses_right_view_func(self):
        path = self.urls.get("customer_list")
        path_operations = router.path_operations.get(path).operations[0]
        view = path_operations.view_func
        self.assertIs(view, customer_list)

    def test_list_for_anonymous_user_returns_401_status_code(self):
        resp = self.guest_client.get(self.urls.get("customer_list"))
        self.assertEqual(resp.status_code, HTTPStatus.UNAUTHORIZED)

    def test_list_for_usual_user_returns_401_status_code(self):
        resp = self.user_client.get(self.urls.get("customer_list"))
        self.assertEqual(resp.status_code, HTTPStatus.UNAUTHORIZED)

    def test_list_for_admin_user_returns_200_status_code(self):
        resp = self.admin_client.get(self.urls.get("customer_list"))
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_list_returns_paginagted_result(self):
        from django.conf import settings

        resp = self.admin_client.get(self.urls.get("customer_list"))
        self.assertIn("items", resp.json())
        num_items = resp.json().get("count")
        self.assertEqual(num_items, settings.NINJA_PAGINATION_PER_PAGE)

    def test_list_returns_all_customers(self):
        resp = self.admin_client.get(self.urls.get("customer_list"))
        self.assertEqual(resp.json().get("count"), USER_NUM)

    def test_list_all_response_items_follow_specific_schema(self):
        schema = CustomerOut
        resp = self.admin_client.get(self.urls.get("customer_list"))
        data = resp.json().get("items")

        # In a response Ninja's Schema automatically replaces submodel attributes
        # like `user.username` with a given attribute name like `username`.
        # But to validate the output result we need to bring those dotted
        # attributes to their initial place.
        # Need to work this out later.
        for item in data:
            item["user.username"] = item.pop("username")
            item["user.email"] = item.pop("email")
        self.assertTrue(all(schema(**item) for item in data))

    def test_list_returns_empty_list_when_no_customer_exists(self):
        Customer.objects.all().delete()
        resp = self.admin_client.get(self.urls.get("customer_list"))
        self.assertEqual(resp.json().get("items"), [])

    ### CUSTOMER CREATE SECTION ###
    def test_create_uses_right_view_func(self):
        path = self.urls.get("customer_create")
        path_operations = router.path_operations.get(path).operations[0]
        view = path_operations.view_func
        self.assertIs(view, customer_create)

    def test_create_for_anonymous_user_returns_401_status_code(self):
        resp = self.guest_client.post(
            self.urls.get("customer_create"), json={}
        )
        self.assertEqual(resp.status_code, HTTPStatus.UNAUTHORIZED)

    def test_create_for_usual_user_returns_401_status_code(self):
        resp = self.user_client.post(self.urls.get("customer_create"), json={})
        self.assertEqual(resp.status_code, HTTPStatus.UNAUTHORIZED)

    def test_create_for_admin_with_valid_payload_returns_200_status_code(self):
        payload = {
            "username": "bobby",
            "email": "bobby@hello.py",
            "password": "aaaaa",
            "status": "activated",
            "is_active": True,
            "first_name": "BOB",
        }
        resp = self.admin_client.post(
            self.urls.get("customer_create"), json=payload
        )
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_create_with_missing_username_returns_422_status_code(self):
        payload = {
            "email": "bobby@hello.py",
            "password": "aaaaa",
            "status": "activated",
            "is_active": True,
            "first_name": "BOB",
        }
        resp = self.admin_client.post(
            self.urls.get("customer_create"), json=payload
        )
        self.assertEqual(resp.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

    def test_create_with_missing_email_returns_422_status_code(self):
        payload = {
            "username": "bobby",
            "password": "aaaaa",
            "status": "activated",
            "is_active": True,
            "first_name": "BOB",
        }
        resp = self.admin_client.post(
            self.urls.get("customer_create"), json=payload
        )
        self.assertEqual(resp.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

    def test_create_with_empty_payload_returns_422_status_code(self):
        payload = {}
        resp = self.admin_client.post(
            self.urls.get("customer_create"), json=payload
        )
        self.assertEqual(resp.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

    def test_create_with_valid_payload_creates_new_customer(self):
        initial_customer_num = Customer.objects.count()
        payload = {
            "username": "new_user",
            "email": "new_user@hello.py",
            "password": "hello",
            "status": "activated",
            "is_active": True,
            "first_name": "Neo",
        }
        self.admin_client.post(self.urls.get("customer_create"), json=payload)
        self.assertEqual(initial_customer_num + 1, Customer.objects.count())

    def test_create_with_valid_payload_creates_new_user(self):
        initial_user_num = User.objects.count()
        payload = {
            "username": "new_user",
            "email": "new_user@hello.py",
            "password": "hello",
            "status": "activated",
            "is_active": True,
            "first_name": "Neo",
        }
        self.admin_client.post(self.urls.get("customer_create"), json=payload)
        self.assertEqual(initial_user_num + 1, User.objects.count())

    def test_create_does_not_create_new_user_if_it_alerady_exists(self):
        payload = {
            "username": "new_user",
            "email": "new_user@hello.py",
            "password": "hello",
            "is_active": True,
            "first_name": "Neo",
        }
        User.objects.create_user(**payload)
        user_num = User.objects.count()

        payload["status"] = "activated"
        self.admin_client.post(self.urls.get("customer_create"), json=payload)
        self.assertEqual(user_num, User.objects.count())

    def test_create_with_occupied_username_returns_400_status_code(self):
        existing = Customer.objects.first()
        payload = {
            "username": existing.username,
            "email": "new_user@hello.py",
            "password": "hello",
        }
        resp = self.admin_client.post(
            self.urls.get("customer_create"), json=payload
        )
        self.assertEqual(resp.status_code, HTTPStatus.BAD_REQUEST)

    def test_create_with_occupied_email_returns_400_status_code(self):
        existing = Customer.objects.first()
        payload = {
            "username": "new_user",
            "email": existing.email,
            "password": "hello",
        }
        resp = self.admin_client.post(
            self.urls.get("customer_create"), json=payload
        )
        self.assertEqual(resp.status_code, HTTPStatus.BAD_REQUEST)

    ### CUSTOMER DETAIL SECTION ###
    def test_detal_uses_right_view_func(self):
        path = self.urls.get("customer_detail")
        path_operations = router.path_operations.get(path).operations[0]
        view = path_operations.view_func
        self.assertIs(view, customer_detail)

    def test_detail_for_anonymous_user_returns_401_status_code(self):
        customer = self.customers[0]
        resp = self.guest_client.get(
            self.urls.get("customer_detail").format(id=customer.id)
        )
        self.assertEqual(resp.status_code, HTTPStatus.UNAUTHORIZED)

    def test_detail_for_usual_user_returns_401_status_code(self):
        customer = self.customers[0]
        resp = self.user_client.get(
            self.urls.get("customer_detail").format(id=customer.id)
        )
        self.assertEqual(resp.status_code, HTTPStatus.UNAUTHORIZED)

    def test_detail_with_valid_id_returns_200_status_code_for_admin(self):
        customer = self.customers[0]
        resp = self.admin_client.get(
            self.urls.get("customer_detail").format(id=customer.id)
        )
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_detail_with_invalid_id_returns_404_status_code(self):
        invalid_id = -1
        resp = self.admin_client.get(
            self.urls.get("customer_detail").format(id=invalid_id)
        )
        self.assertEqual(resp.status_code, HTTPStatus.NOT_FOUND)

    def test_detail_with_wrong_type_id_returns_422_status_code(self):
        wrong_type_id = "wrong"
        resp = self.admin_client.get(
            self.urls.get("customer_detail").format(id=wrong_type_id)
        )
        self.assertEqual(resp.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

    def test_detail_returns_non_sequence(self):
        from typing import Sequence

        customer = self.customers[0]
        resp = self.admin_client.get(
            self.urls.get("customer_detail").format(id=customer.id)
        )
        self.assertNotIsInstance(resp.json(), Sequence)

    def test_detail_response_contains_keys_from_schema(self):
        schema = CustomerOut.schema(by_alias=False)
        expected_keys = schema.get("properties").keys()
        customer = self.customers[0]
        resp = self.admin_client.get(
            self.urls.get("customer_detail").format(id=customer.id)
        )
        self.assertEqual(resp.json().keys(), expected_keys)

    def test_detail_response_dict_follow_specific_schema(self):
        customer = self.customers[0]
        resp = self.admin_client.get(
            self.urls.get("customer_detail").format(id=customer.id)
        )
        resp_data = resp.json().copy()
        resp_data["user.username"] = resp_data.pop("username")
        resp_data["user.email"] = resp_data.pop("email")
        self.assertTrue(CustomerOut(**resp_data))

    ### CUSTOMER UPDATE SECTION ###
    def test_update_uses_right_func(self):
        path = self.urls.get("customer_update")
        path_operations = router.path_operations.get(path).operations[0]
        view = path_operations.view_func
        self.assertIs(view, customer_update)

    def test_update_for_anonymous_user_returns_401_status_code(self):
        customer = self.customers[0]
        resp = self.guest_client.put(
            self.urls.get("customer_update").format(id=customer.id), json={}
        )
        self.assertEqual(resp.status_code, HTTPStatus.UNAUTHORIZED)

    def test_update_for_usual_user_returns_401_status_code(self):
        customer = self.customers[0]
        resp = self.user_client.put(
            self.urls.get("customer_update").format(id=customer.id), json={}
        )
        self.assertEqual(resp.status_code, HTTPStatus.UNAUTHORIZED)

    def test_update_with_invalid_payload_returns_422_status_code(self):
        customer = Customer.objects.first()
        payload = {"invalid_smth_": "invalid-invalid"}
        resp = self.admin_client.put(
            self.urls.get("customer_update").format(id=customer.id),
            json=payload,
        )
        self.assertEqual(resp.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

    def test_update_with_empty_payload_returns_400_status_code(self):
        customer = Customer.objects.first()
        payload = {}
        resp = self.admin_client.put(
            self.urls.get("customer_update").format(id=customer.id),
            json=payload,
        )
        self.assertEqual(resp.status_code, HTTPStatus.BAD_REQUEST)

    def test_update_with_invalid_customer_id_returns_404_status_code(self):
        id = -1
        payload = {"email": "new_email@hello.py"}
        resp = self.admin_client.put(
            self.urls.get("customer_update").format(id=id), json=payload
        )
        self.assertEqual(resp.status_code, HTTPStatus.NOT_FOUND)

    def test_update_with_invalid_email_returns_422_status_code(self):
        customer = Customer.objects.first()
        payload = {"email": "invalid_new_email"}
        resp = self.admin_client.put(
            self.urls.get("customer_update").format(id=customer.id),
            json=payload,
        )
        self.assertEqual(resp.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

    def test_update_with_valid_payload_returns_200_status_code(self):
        customer = Customer.objects.first()
        payload = {"email": "new_email@hello.py"}
        resp = self.admin_client.put(
            self.urls.get("customer_update").format(id=customer.id),
            json=payload,
        )
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_update_with_valid_payload_updates_customer_and_user_attrs(self):
        customer = Customer.objects.first()
        user = User.objects.get(id=customer.id)
        payload = {
            "email": "new_email@hello.py",
            "first_name": "sam",
            "last_name": "smith",
            "phone_number": "80000000000",
        }
        self.admin_client.put(
            self.urls.get("customer_update").format(id=customer.id),
            json=payload,
        )
        customer.refresh_from_db()
        user.refresh_from_db()
        self.assertEqual(customer.phone_number, payload["phone_number"])
        self.assertEqual(user.email, payload["email"])
        self.assertEqual(user.first_name, payload["first_name"])
        self.assertEqual(user.last_name, payload["last_name"])

    def test_update_with_occupied_email_returns_400_status_code(self):
        customer = Customer.objects.first()
        another_customer = Customer.objects.last()
        payload = {"email": another_customer.email}
        resp = self.admin_client.put(
            self.urls.get("customer_update").format(id=customer.id),
            json=payload,
        )
        self.assertEqual(resp.status_code, HTTPStatus.BAD_REQUEST)

    def test_update_with_occupied_email_response_contains_error_message(self):
        customer = Customer.objects.first()
        another_customer = Customer.objects.last()
        payload = {"email": another_customer.email}
        resp = self.admin_client.put(
            self.urls.get("customer_update").format(id=customer.id),
            json=payload,
        )
        self.assertIn("error_message", resp.json())
        self.assertIn("email", resp.json().get("error_message"))

    ### CUSTOMER DELETE SECTION ###
    def test_delete_uses_right_func(self):
        path = self.urls.get("customer_delete")
        path_operations = router.path_operations.get(path).operations[0]
        view = path_operations.view_func
        self.assertIs(view, customer_delete)

    def test_delete_for_anonymous_user_returns_401_status_code(self):
        customer = self.customers[0]
        resp = self.guest_client.delete(
            self.urls.get("customer_delete").format(id=customer.id)
        )
        self.assertEqual(resp.status_code, HTTPStatus.UNAUTHORIZED)

    def test_delete_for_usual_user_returns_401_status_code(self):
        customer = self.customers[0]
        resp = self.user_client.delete(
            self.urls.get("customer_delete").format(id=customer.id)
        )
        self.assertEqual(resp.status_code, HTTPStatus.UNAUTHORIZED)

    def test_delete_with_invalid_id_returns_404_status_code(self):
        invalid_id = -1
        resp = self.admin_client.delete(
            self.urls.get("customer_delete").format(id=invalid_id)
        )
        self.assertEqual(resp.status_code, HTTPStatus.NOT_FOUND)

    def test_delete_with_valid_id_returns_200_status_code(self):
        customer = Customer.objects.first()
        resp = self.admin_client.delete(
            self.urls.get("customer_delete").format(id=customer.id)
        )
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_delete_with_valid_id_does_not_delete_customer(self):
        customer_num = Customer.objects.count()
        customer = Customer.objects.first()
        self.admin_client.delete(
            self.urls.get("customer_delete").format(id=customer.id)
        )
        self.assertEqual(customer_num, Customer.objects.count())

    def test_delete_with_valid_id_changes_customer_status_to_archived(self):
        customer = Customer.objects.first()
        customer.status = "foo"
        customer.save(update_fields=["status"])
        self.admin_client.delete(
            self.urls.get("customer_delete").format(id=customer.id)
        )
        customer.refresh_from_db()
        self.assertEqual(customer.status, Customer.CustomerStatus.ARCHIVED)

    def test_delete_with_valid_id_changes_user_is_active_to_false(self):
        customer = Customer.objects.first()
        customer.status = "foo"
        customer.save(update_fields=["status"])
        self.admin_client.delete(
            self.urls.get("customer_delete").format(id=customer.id)
        )
        user = User.objects.get(customer=customer)
        self.assertFalse(user.is_active)
