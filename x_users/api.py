import logging
from typing import List

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from ninja import Router

from .schemas import Message, UserIn, UserOut

logger = logging.getLogger(__name__)

router = Router()
User = get_user_model()

"""
# @router.api_operation(
#    ("GET", "POST"),
#    "/",
#    url_name="user_list",
#    response={200: List[UserOut], 201: UserIn},
# )
@router.api_operation(
    ("GET", "POST"),
    "/",
    url_name="user_list",
    response={200: List[UserOut], 201: UserOut},
)
def user_list(request, payload: UserIn):
    # print(dir(request))
    logger.warning("HERE")
    if request.method == "GET":
        return User.objects.all()
    elif request.method == "POST":
        print("works")
        user = User.objects.create_user(**payload.dict())
        return user
    #    print(dir(response))
"""


@router.get("/", response=List[UserOut], url_name="user_list")
def user_list(request):
    return User.objects.all()


@router.get("/{id}/", response=UserOut, url_name="user_detail")
def user_detail(request, id: int):
    return get_object_or_404(User, pk=id)


@router.post(
    "/create", response={201: UserOut, 400: Message}, url_name="user_create"
)
def user_create(request, payload: UserIn):
    try:
        user, _ = User.objects.get_or_create(**payload.dict())
    except IntegrityError:
        logger.info("Instance duplication attempt", exc_info=1)
        return 400, {"message": "Instance with such attributes already exists"}
    return user


@router.put("/{id}/update", response=UserOut, url_name="user_update")
def user_update(request, id: int, payload: UserIn):
    user = get_object_or_404(User, pk=id)
    for attr, value in payload.dict().items():
        setattr(user, attr, value)
    user.save()
    return user
