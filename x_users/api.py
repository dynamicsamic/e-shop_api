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

from .schemas import UserIn, UserOut, UserUpdate

logger = logging.getLogger(__name__)

router = Router()
User = get_user_model()


@router.get("/", response=List[UserOut], url_name="user_list")
def user_list(request):
    return User.objects.all()


@router.get("/{id}/", response=UserOut, url_name="user_detail")
def user_detail(request, id: int):
    return get_object_or_404(User, id=id)


@router.post(
    "/create",
    response={200: UserOut, 400: ErrorMessage},
    url_name="user_create",
)
def user_create(request, payload: UserIn):
    data = payload.dict()
    username = data.get("username")
    email = data.get("email")
    if User.objects.filter(Q(username=username) | Q(email=email)).exists():
        logger.info("Instance duplication attempt")
        return 400, {
            "error_message": "Instance with such attributes already exists"
        }
    return User.objects.create_user(**data)


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
