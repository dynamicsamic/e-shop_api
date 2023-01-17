from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect
from ninja import Path, Router
from ninja.errors import HttpError

from utils import trim_attr_name_from_integrity_error
from x_auth.authentication import get_token
from x_users.schemas import UserIn

from .authentication import JWToken
from .email import send_activation_email
from .schemas import CredentialsIn, PathToken, TokenOut

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
    # need to create user simultaneously: create_customer=True
    # maybe need to return user or customer instance as response?
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


@router.post("/activate/{token}", url_name="user_activate")
def activate(request, token: PathToken = Path(...)):
    jwt_checker = JWToken()
    decoded = jwt_checker._decode(token)
    if decoded is None:
        raise HttpError(401, "invalid token")

    user = get_object_or_404(User, id=decoded.get("user_id"))
    if not jwt_checker._validate_exp_time(decoded):
        new_token = jwt_checker.generate_token(user)
        send_activation_email(user.get_username(), user.email, new_token)
        raise HttpError(
            401,
            {"token has expired": f"Another token  was sent to {user.email}"},
        )
    user.is_active = True
    user.save(update_fields=("is_active",))
    return {"success": f"user {user.get_username()} activated!"}


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
