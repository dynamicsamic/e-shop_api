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


class BasicAuthBearer(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str):
        pass

    def _get_user(self, token: str) -> Union["User", "AnonymousUser"]:
        """Get user from jwt token. Return `AnonymousUser` if no user found."""
        payload = self._decode(token)
        if not self._validate_exp_time(payload):
            raise HttpError(
                401, {"token validation error": "token has expired"}
            )
        user_id = payload.get("user_id", -1)
        user = User.objects.filter(id=user_id).first()
        return user or AnonymousUser()

    def _decode(self, token: str) -> Union[dict[str, Any], HttpError]:
        """Decode token. Raise exception if invalid."""
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except DecodeError as e:
            raise HttpError(401, {"invalid token format": f"{e}"})

    def _validate_exp_time(self, payload: dict[str, Any]) -> bool:
        """Check expiration time recieved from decoded token."""
        exp_time = payload.get("exp_time")
        if exp_time is None:
            raise HttpError(
                401,
                {
                    "token validation error: "
                    "`exp_time` must be present in decoded payload"
                },
            )

        exp_time = float(exp_time)
        timestamp = dt.datetime.timestamp(dt.datetime.now())
        return exp_time > timestamp


class StaffOnlyAuthBearer(BasicAuthBearer):
    def authenticate(self, request: HttpRequest, token: str):
        user = self._get_user(token)
        return user.is_staff


class AuthenticatedOnlyAuthBearer(BasicAuthBearer):
    def authenticate(self, request: HttpRequest, token: str):
        return bool(self._get_user(token))


def get_token(obj: "User") -> str:
    """Return jwt token."""
    now_ts = dt.datetime.timestamp(dt.datetime.now())
    payload = {"user_id": obj.id, "exp_time": now_ts + settings.TOKEN_EXP_TIME}
    return jwt.encode(payload, settings.SECRET_KEY)


class JWToken:
    generate_token = get_token

    def _get_user(self, token: str) -> Union["User", "AnonymousUser"]:
        """Get user from jwt token. Return `AnonymousUser` if no user found."""
        user = None
        if payload := self._decode(token):
            if self._validate_exp_time(payload):
                user_id = payload.get("user_id", -1)
                user = User.objects.filter(id=user_id).first()
        return user or AnonymousUser()

    def _decode(self, token: str) -> Union[dict[str, Any], HttpError]:
        """Decode token. Raise exception if invalid."""
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except DecodeError as e:
            return None
            raise HttpError(401, {"invalid token format": f"{e}"})

    def _validate_exp_time(self, payload: dict[str, Any]) -> bool:
        """Check expiration time recieved from decoded token."""
        exp_time = payload.get("exp_time")
        if exp_time is None:
            return False
        exp_time = float(exp_time)
        timestamp = dt.datetime.timestamp(dt.datetime.now())
        return exp_time > timestamp
