from http import HTTPStatus

from django.conf import settings
from django.test import TestCase
from ninja.testing import TestClient

from tests.clients import AuthClient
from tests.factories import VendorFactory
from tests.utils import (
    get_ninja_view_from_router,
    get_ninja_view_from_router_paginated,
)

from .api import router, vendor_list
from .models import Vendor

VENDOR_NUM = 10


class CreateVendorsMixin:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendors = VendorFactory.create_batch(VENDOR_NUM)
        cls.guest_client = TestClient(router)
        cls.urls = {"list": "/"}


class VendorsApiTestCase(CreateVendorsMixin, TestCase):
    # VENDOR LIST SECTION
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
        first_five_ids = [i.get("id") for i in items]
        self.assertEqual(first_five_ids, list(range(1, new_page_size + 1)))

    def test_list_returns_all_vendors(self):
        vendor_num = Vendor.objects.count()
        self.assertEqual(vendor_num, VENDOR_NUM)
        resp = self.guest_client.get(self.urls.get("list"))
        self.assertEqual(resp.json().get("count"), vendor_num)
