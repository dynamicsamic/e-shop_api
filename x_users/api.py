import logging
from typing import List

from django.contrib.auth import get_user_model
from django.http.response import HttpResponse
from django.urls import reverse_lazy
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


@router.post("/create", response=UserOut, url_name="user_create")
def user_create(request, payload: UserIn):
    user = User.objects.create_user(**payload.dict())
    # user, _ = User.objects.get_or_create(**payload.dict())
    return user
