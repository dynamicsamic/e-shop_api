from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from ninja.testing import TestClient

from tests.clients import AuthClient
from tests.factories import VendorFactory
from tests.utils import (
    get_ninja_view_from_router,
    get_ninja_view_from_router_paginated,
)
from x_auth.authentication import generate_user_token

from .api import router, vendor_create, vendor_detail, vendor_list
from .models import Vendor
from .schemas import VendorOut

User = get_user_model()
VENDOR_NUM = 10


class CreateVendorsMixin:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendors = VendorFactory.create_batch(VENDOR_NUM)
        cls.guest_client = TestClient(router)
        cls.urls = {"list": "/", "create": "/create", "detail": "/{slug}/"}
        cls.vendor = cls.vendors[0]
        cls.admin = User.objects.create_superuser(
            username="admin", email="admin@hello.py", password="hello"
        )
        cls.admin_client = AuthClient(router, generate_user_token(cls.admin))


class VendorsApiTestCase(CreateVendorsMixin, TestCase):
    ### VENDOR LIST SECTION ###
    def test_list_uses_right_view(self):
        path = self.urls.get("list")
        view = get_ninja_view_from_router_paginated(router, path)
        self.assertIs(view, vendor_list)

    def test_list_returns_200_status_code(self):
        resp = self.guest_client.get(self.urls.get("list"))
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_list_returns_paginated_result(self):
        resp = self.guest_client.get(self.urls.get("list"))
        self.assertIn("items", resp.json())

    def test_list_returns_first_page_if_set_in_request(self):
        new_page_size = 5
        path = self.urls.get("list")
        view = get_ninja_view_from_router(router, path)
        paginator = view.__closure__[1].cell_contents
        paginator.page_size = new_page_size
        resp = self.guest_client.get(f"{path}?page=1")
        items = resp.json().get("items")
        self.assertEqual(len(items), new_page_size)

        ids_expected = list(range(1, new_page_size + 1))
        ids_recieved = [i.get("id") for i in items]
        self.assertEqual(ids_expected, ids_recieved)

    def test_list_returns_second_page_if_set_in_request(self):
        new_page_size = 5
        path = self.urls.get("list")
        view = get_ninja_view_from_router(router, path)
        paginator = view.__closure__[1].cell_contents
        paginator.page_size = new_page_size
        resp = self.guest_client.get(f"{path}?page=2")
        items = resp.json().get("items")
        self.assertEqual(len(items), new_page_size)

        ids_expected = list(range(new_page_size + 1, new_page_size * 2 + 1))
        ids_recieved = [i.get("id") for i in items]
        self.assertEqual(ids_expected, ids_recieved)

    def test_list_returns_all_vendors(self):
        vendor_num = Vendor.objects.count()
        self.assertEqual(vendor_num, VENDOR_NUM)
        resp = self.guest_client.get(self.urls.get("list"))
        self.assertEqual(resp.json().get("count"), vendor_num)

    def test_list_response_objects_follow_defined_schema(self):
        expected_keys = VendorOut.schema().get("properties").keys()
        resp = self.guest_client.get(self.urls.get("list"))
        for item in resp.json().get("items"):
            self.assertEqual(item.keys(), expected_keys)

    ### VENDOR DETAIL SECTION ###
    def test_detail_uses_right_view(self):
        path = self.urls.get("detail")
        view = get_ninja_view_from_router(router, path)
        self.assertEqual(view, vendor_detail)

    def test_detail_with_valid_slug_returns_200_status_code(self):
        path = self.urls.get("detail").format(slug=self.vendor.slug)
        resp = self.guest_client.get(path)
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_detail_with_valid_slug_returns_selected_vendor(self):
        path = self.urls.get("detail").format(slug=self.vendor.slug)
        resp = self.guest_client.get(path)
        attrs_expected = self.vendor.__dict__.copy()
        attrs_expected.pop("_state")
        attrs_recieved = resp.json().items()
        self.assertEqual(attrs_recieved, attrs_expected.items())

    def test_detail_with_invalid_slug_returns_404_status_code(self):
        invalid_slug = "invalid-invalid"
        path = self.urls.get("detail").format(slug=invalid_slug)
        resp = self.guest_client.get(path)
        self.assertEqual(resp.status_code, HTTPStatus.NOT_FOUND)

    def test_detail_response_object_follow_defined_schema(self):
        expected_keys = VendorOut.schema().get("properties").keys()
        path = self.urls.get("detail").format(slug=self.vendor.slug)
        resp = self.guest_client.get(path)
        self.assertEqual(resp.json().keys(), expected_keys)

    # VENDOR CREATE SECTION
    def test_create_uses_right_view(self):
        path = self.urls.get("create")
        view = get_ninja_view_from_router(router, path)
        self.assertEqual(view, vendor_create)

    def test_create_for_anonymous_user_returns_401_status_code(self):
        payload = {"name": "new vendor", "description": "lorem ipsum"}
        resp = self.guest_client.post(self.urls.get("create"), json=payload)
        self.assertEqual(resp.status_code, HTTPStatus.UNAUTHORIZED)

    def test_create_for_admin_returns_201_status_code(self):
        payload = {"name": "new vendor", "description": "lorem ipsum"}
        resp = self.admin_client.post(self.urls.get("create"), json=payload)
        self.assertEqual(resp.status_code, HTTPStatus.CREATED)

    def test_create_with_valid_payload_creates_vendor(self):
        vendor_num_initial = Vendor.objects.count()
        payload = {"name": "new vendor", "description": "lorem ipsum"}
        self.admin_client.post(self.urls.get("create"), json=payload)
        vendor_num_current = Vendor.objects.count()
        self.assertEqual(vendor_num_current, vendor_num_initial + 1)

    def test_create_generates_new_vendor_with_given_attrs(self):
        payload = {"name": "new vendor", "description": "lorem ipsum"}
        self.admin_client.post(self.urls.get("create"), json=payload)
        new_vendor = Vendor.objects.get(name=payload["name"])
        self.assertTrue(new_vendor.name, payload["name"])
        self.assertTrue(new_vendor.description, payload["description"])

    def test_create_response_object_follow_defined_schema(self):
        expected_keys = VendorOut.schema().get("properties").keys()
        payload = {"name": "new vendor", "description": "lorem ipsum"}
        resp = self.admin_client.post(self.urls.get("create"), json=payload)
        self.assertEqual(resp.json().keys(), expected_keys)

    def test_create_without_payload_returns_422_status_code(self):
        payload = {}
        resp = self.admin_client.post(self.urls.get("create"), json=payload)
        self.assertEqual(resp.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

    def test_create_with_missing_payload_value_returns_422_status_code(self):
        payload = {"name": "new vendor"}
        resp = self.admin_client.post(self.urls.get("create"), json=payload)
        self.assertEqual(resp.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

    def test_create_with_occupied_name_returns_400_status_code(self):
        payload = {"name": self.vendor.name, "description": "lorem ipsum"}
        resp = self.admin_client.post(self.urls.get("create"), json=payload)
        self.assertEqual(resp.status_code, HTTPStatus.BAD_REQUEST)
