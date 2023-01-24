from typing import List

from ninja import Router
from ninja.pagination import PageNumberPagination, paginate

from .models import Vendor
from .schemas import VendorOut

router = Router()


@router.get("/", response=List[VendorOut], url_name="vendor_list")
@paginate(PageNumberPagination)
def vendor_list(request):
    return Vendor.objects.all()
