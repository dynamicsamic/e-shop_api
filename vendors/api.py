import logging
from typing import List

from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import PageNumberPagination, RouterPaginated, paginate

from db.schemas import ErrorMessage
from utils import SlugSchema, trim_attr_name_from_integrity_error
from x_auth.authentication import StaffOnlyAuthBearer

from .models import Vendor
from .schemas import VendorIn, VendorOut, VendorUpdate

# router = Router()
logger = logging.getLogger(__name__)
router = RouterPaginated()


@router.get("/", response=List[VendorOut], url_name="vendor_list")
def vendor_list(request):
    return Vendor.objects.all()


@router.get("/{slug}/", response=VendorOut, url_name="vendor_detail")
def vendor_detail(request, slug: SlugSchema):
    return get_object_or_404(Vendor, **slug.dict())


@router.post(
    "/create",
    response={201: VendorOut, 400: ErrorMessage},
    url_name="vendor_create",
    auth=StaffOnlyAuthBearer(),
)
def vendor_create(request, payload: VendorIn):
    try:
        return Vendor.objects.create(**payload.dict())
    except IntegrityError as e:
        logger.info("Vendor instance duplication attempt")
        return 400, {
            "error_message": "Vendor instance with such name already exists"
        }


@router.put(
    "/{slug}/update",
    response={200: VendorOut, 400: ErrorMessage},
    url_name="vendor_create",
    auth=StaffOnlyAuthBearer(),
)
def vendor_update(request, slug, payload: VendorUpdate):
    valid_data = payload.dict(exclude_unset=True)
    if not valid_data:
        return 400, {"error_message": "Empty request body not allowed"}

    vendor = get_object_or_404(Vendor, slug=slug)
    for attr, value in valid_data.items():
        if attr == "name":
            vendor.slug = None
        setattr(vendor, attr, value)
    try:
        vendor.save()
    except IntegrityError as e:
        occupied_attr = trim_attr_name_from_integrity_error(e)
        logger.info(
            f"Update attempt with attribute {occupied_attr} already in use"
        )

        return 400, {
            "error_message": f"Update error! Attribute {occupied_attr} already in use."
        }
    return vendor
