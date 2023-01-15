from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect
from ninja import Router
from ninja.errors import HttpError

from utils import trim_attr_name_from_integrity_error
from x_auth.authentication import get_token
from x_users.schemas import UserIn

from .email import send_activation_email
from .schemas import CredentialsIn, TokenOut

User = get_user_model()
router = Router()


@router.post("/token", response=TokenOut, url_name="token_create")
def token_create(request, credentials: CredentialsIn):
    username, password = credentials.dict().values()
    user = get_object_or_404(User, username=username)
    if user.check_password(password):
        return {"access_token": get_token(user)}
    raise HttpError(401, "wrong password")


@router.post("/signup", url_name="user_signup")
def signup(request, credentials: UserIn):
    try:
        user = User.objects.create_user(**credentials.dict())
    except IntegrityError as e:
        trouble_attr_name = trim_attr_name_from_integrity_error(e)
        raise HttpError(
            400,
            {
                "error_message": f"Provided {trouble_attr_name} already in use. Please choose another one."
            },
        )
    token = get_token(user)
    send_activation_email(user.username, user.email, token)


"""
1.нажал на ссылку.
2. во вью берем из урла токен
3. декодим токен.
4. Находим юзера.
5. Делаем юзера активным.
6. Возвращаем редирект на главную страницу.
"""

# redirect to main page; need work.
# redirect(...)
