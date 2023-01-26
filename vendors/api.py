from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import PageNumberPagination, RouterPaginated, paginate

from .models import Vendor
from .schemas import VendorOut

# router = Router()
router = RouterPaginated()


@router.get("/", response=List[VendorOut], url_name="vendor_list")
def vendor_list(request):
    return Vendor.objects.all()


@router.get("/{name}", response=VendorOut, url_name="vendor_detail")
def vendor_detail(request, name: str):
    return get_object_or_404(Vendor, name=name)
