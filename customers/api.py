import logging
from typing import List

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import PageNumberPagination, paginate

from db.schemas import ErrorMessage
from utils import trim_attr_name_from_integrity_error
from x_auth.authentication import StaffOnlyAuthBearer

from .models import Customer
from .schemas import CustomerCreate, CustomerOut, CustomerUpdate

User = get_user_model()
logger = logging.getLogger(__name__)
router = Router(auth=StaffOnlyAuthBearer())


@router.get(
    "/",
    response=List[CustomerOut],
    url_name="customer_list",
)
@paginate(PageNumberPagination)
def customer_list(request):
    return Customer.objects.all()


@router.get("/{id}/", response=CustomerOut, url_name="customer_detail")
def customer_detail(request, id: int):
    return get_object_or_404(Customer, id=id)


@router.post(
    "/create",
    response={200: CustomerOut, 400: ErrorMessage},
    url_name="customer_create",
)
def customer_create(request, payload: CustomerCreate):
    user_data = payload.dict()
    customer_data = {
        "status": user_data.pop("status"),
        "phone_number": user_data.pop("phone_number"),
    }
    username = user_data.get("username")
    user_email = user_data.get("email")
    if Customer.objects.filter(
        Q(user__username=username) | Q(user__email=user_email)
    ).exists():
        logger.info("Customer instance duplication attempt")
        return 400, {
            "error_message": "Customer instance with such attributes already exists"
        }

    user = User.objects.filter(
        Q(username=username) | Q(email=user_email)
    ).first()
    if not user:
        user = User.objects.create_user(**user_data)
        logger.info(f"Created User instance with id: {user.id}")
    return Customer.objects.create(user=user, **customer_data)


@router.put(
    "/{id}/update",
    response={200: CustomerOut, 400: ErrorMessage},
    url_name="customer_update",
)
def customer_update(request, id: int, payload: CustomerUpdate):
    customer = get_object_or_404(Customer, id=id)
    valid_data = payload.dict(exclude_unset=True)
    if not valid_data:
        return 400, {"error_message": "Empty request body not allowed"}

    for attr, value in valid_data.items():
        setattr(customer, attr, value)
    try:
        customer.save(update_fields=valid_data.keys())
    except IntegrityError as e:
        trouble_attr = trim_attr_name_from_integrity_error(e)
        logger.warning(f"Trouble with updating attribute `{trouble_attr}`")
        return 400, {
            "error_message": f"Update error! Attribute `{trouble_attr}` may already be in use."
        }
    return customer


@router.delete("/{id}/delete")
def customer_delete(request, id: int):
    customer = get_object_or_404(Customer, id=id)
    if customer.status == Customer.CustomerStatus.ARCHIVED:
        return {
            "warning": f"Customer with id {id} is already in archive;"
            "nothing to change."
        }
    customer.status = "archived"
    # or just customer.user.is_active = False
    User.objects.filter(customer=customer).update(is_active=False)
    customer.save(update_fields=("status",))
    return {
        "success": f"Customer with id {customer.id} was archived,"
        "`is_active` set to False"
    }
