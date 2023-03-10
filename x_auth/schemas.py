from typing import Literal

from ninja import Schema
from pydantic import Field, constr

from utils import LONG_ENOUGH_REGEX


class CredentialsIn(Schema):
    username: constr(regex=LONG_ENOUGH_REGEX)
    password: constr(regex=LONG_ENOUGH_REGEX)


class TokenOut(Schema):
    access_token: str = Field(..., min_length=90)


class PathToken(Schema):
    token: constr(regex=r"[0-9A-Za-z.]+")

    @property
    def value(self):
        return self.token
