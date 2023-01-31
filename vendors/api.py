import logging
from typing import List

from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import PageNumberPagination, RouterPaginated, paginate

from db.schemas import ErrorMessage
from utils import SlugSchema
from x_auth.authentication import StaffOnlyAuthBearer

from .models import Vendor
from .schemas import VendorIn, VendorOut

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


@router.put("/{slug}/update", url_name="vendor_create")
def vendor_update(request, slug):
    pass
