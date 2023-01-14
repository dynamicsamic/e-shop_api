import datetime as dt

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError

from x_auth.authentication import get_token

from .schemas import CredentialsIn

User = get_user_model()
router = Router()


@router.post("/token", url_name="token_create")
def token_create(request, credentials: CredentialsIn):
    username, password = credentials.dict().values()
    user = get_object_or_404(User, username=username)
    if user.check_password(password):
        return get_token(user)
    raise HttpError(401, "wrong password")
