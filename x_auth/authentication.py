import datetime as dt
from typing import Any, Literal, Union

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db.models import Model
from django.http import HttpRequest
from jwt.exceptions import DecodeError
from ninja.errors import HttpError
from ninja.security import HttpBearer

User = get_user_model()


def decode_jwtoken(token: str) -> dict[str, Any] | DecodeError:
    """
    Decode jwtoken and return decoded `payload: dict`.
    Return `DecodeError` if token invalid.
    """
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )
    except DecodeError as e:
        return e


def validate_token_exp_time(payload: dict[str, Any]) -> bool:
    """Check expiration time recieved from decoded token."""
    exp_time = payload.get("exp_time", 0)
    try:
        exp_time = float(exp_time)
    except ValueError:
        return False
    timestamp = dt.datetime.timestamp(dt.datetime.now())
    return exp_time > timestamp


def generate_user_token(user: "User") -> str:
    """Generate jwt token for user."""
    now_ts = dt.datetime.timestamp(dt.datetime.now())
    payload = {
        "user_id": user.id,
        "exp_time": now_ts + settings.TOKEN_EXP_TIME,
    }
    return jwt.encode(payload, settings.SECRET_KEY)


class BasicAuthBearer(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str):
        pass

    def get_user(self, token: str) -> Union["User", "AnonymousUser"]:
        """Get user from jwt token. Return `AnonymousUser` if no user found."""
        payload = decode_jwtoken(token)
        if isinstance(payload, Exception):
            raise HttpError(401, {"invalid token format": f"{payload}"})

        if not validate_token_exp_time(payload):
            raise HttpError(
                401, {"token validation error": "token has expired"}
            )
        user_id = payload.get("user_id", -1)
        user = User.objects.filter(id=user_id).first()
        return user or AnonymousUser()


class StaffOnlyAuthBearer(BasicAuthBearer):
    def authenticate(self, request: HttpRequest, token: str):
        user = self.get_user(token)
        return user.is_staff


class AuthenticatedOnlyAuthBearer(BasicAuthBearer):
    def authenticate(self, request: HttpRequest, token: str):
        return bool(self.get_user(token))
