import logging
from typing import List

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from ninja import Router

from db.schemas import ErrorMessage
from utils import trim_attr_name_from_integrity_error

from .models import Customer
from .schemas import CustomerCreate, CustomerOut, CustomerUpdate

logger = logging.getLogger(__name__)

router = Router()
User = get_user_model()


@router.get("/", response=List[CustomerOut], url_name="customer_list")
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
        return 400, {"error_message": "Empty request body now allowed"}
    return customer


"""

@router.put(
    "/{id}/update",
    response={200: UserOut, 400: ErrorMessage},
    url_name="user_update",
)
def user_update(request, id: int, payload: UserUpdate):
    user = get_object_or_404(User, id=id)

    for attr, value in payload.dict().items():
        setattr(user, attr, value)
    try:
        user.save(update_fields=payload.dict().keys())
    except IntegrityError as e:
        occupied_attr = trim_attr_name_from_integrity_error(e)
        logger.info(
            f"Update attempt with attribute {occupied_attr} already in use"
        )

        return 400, {
            "error_message": f"Update error! Attribute {occupied_attr} already in use."
        }
    return user


@router.delete("/{id}/delete")
def user_delete(request, id: int):
    user = get_object_or_404(User, id=id)
    user.delete()
    return {"success": f"User with id {id} was deleted"}
"
"""
