from typing import List

from django.contrib.auth import get_user_model
from ninja import Router

from .schemas import UserIn, UserOut

router = Router()
User = get_user_model()


@router.get("/", response=List[UserOut])
def list_users(request):
    return User.objects.all()


@router.post("/", response=UserOut)
def create_user(request, payload: UserIn):
    user = User.objects.create_user(**payload.dict())
    return user
