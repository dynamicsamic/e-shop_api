from http import HTTPStatus

from django.conf import settings
from django.test import TestCase, override_settings
from ninja.testing import TestClient

from tests.clients import AuthClient
from tests.factories import VendorFactory

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
        settings.NINJA_PAGINATION_PER_PAGE = 5


class VendorsApiTestCase(CreateVendorsMixin, TestCase):
    # VENDOR LIST SECTION
    def test_list_uses_right_view(self):
        path = self.urls.get("list")
        path_operations = router.path_operations.get(path).operations[0]
        view = path_operations.view_func
        self.assertIs(view, vendor_list)

    def test_list_returns_200_status_code(self):
        resp = self.guest_client.get(self.urls.get("list"))
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    @override_settings(INSTALLED_APPS="")
    def test_list_returns_paginated_result(self):

        print(settings.NINJA_PAGINATION_PER_PAGE)
        resp = self.guest_client.get(self.urls.get("list"))
        self.assertIn("items", resp.json())
        print(resp.json())

    def test_list_returns_second_page_if_set_in_request(self):
        f'{self.urls.get("list")}?page=2'

    def test_list_returns_all_vendors(self):
        vendor_num = Vendor.objects.count()
        self.assertEqual(vendor_num, VENDOR_NUM)
        resp = self.guest_client.get(self.urls.get("list"))
        self.assertEqual(resp.json().get("count"), vendor_num)
