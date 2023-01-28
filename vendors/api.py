from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import PageNumberPagination, RouterPaginated, paginate

from utils import SlugSchema
from x_auth.authentication import StaffOnlyAuthBearer

from .models import Vendor
from .schemas import VendorIn, VendorOut

# router = Router()
router = RouterPaginated()


@router.get("/", response=List[VendorOut], url_name="vendor_list")
def vendor_list(request):
    return Vendor.objects.all()


@router.get("/{slug}/", response=VendorOut, url_name="vendor_detail")
def vendor_detail(request, slug: SlugSchema):
    return get_object_or_404(Vendor, **slug.dict())


@router.post("/create", url_name="vendor_create", auth=StaffOnlyAuthBearer())
def vendor_create(request, payload: VendorIn):
    pass
