import logging

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from ninja import Path, Router
from ninja.errors import HttpError

from utils import trim_attr_name_from_integrity_error
from x_users.schemas import UserIn

from .authentication import (
    decode_jwtoken,
    generate_user_token,
    validate_token_exp_time,
)
from .email import send_activation_email
from .schemas import CredentialsIn, PathToken, TokenOut

User = get_user_model()
logger = logging.getLogger(__name__)
router = Router()


@router.post("/token", response=TokenOut, url_name="token_create")
def token_create(request, credentials: CredentialsIn):
    username, password = credentials.dict().values()
    user = get_object_or_404(User, username=username)
    if user.check_password(password):
        return {"access_token": generate_user_token(user)}
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
    token = generate_user_token(user)
    sent = send_activation_email(user.username, user.email, token)
    if not sent:
        logger.error("email dispatch failure! need fix")


@router.post("/activate/{token}", url_name="user_activate")
def activate(request, token: PathToken = Path(...)):
    payload = decode_jwtoken(token.value)
    if isinstance(payload, Exception):
        raise HttpError(401, {"invalid token format": f"{payload}"})

    user = get_object_or_404(User, id=payload.get("user_id"))
    if user.is_active:
        return {
            "nothing to change": f"user {user.get_username()} is already active"
        }
    if not validate_token_exp_time(payload):
        new_token = generate_user_token(user)
        sent = send_activation_email(
            user.get_username(), user.email, new_token
        )
        if not sent:
            logger.error("email dispatch failure! need fix")
        raise HttpError(
            401,
            {"token has expired": f"Another token  was sent to {user.email}"},
        )
    user.is_active = True
    user.save(update_fields=("is_active",))
    return {"success": f"user {user.get_username()} activated!"}
