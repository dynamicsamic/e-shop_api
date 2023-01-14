from ninja import Schema
from pydantic import constr

from utils import LONG_ENOUGH_REGEX


class CredentialsIn(Schema):
    username: constr(regex=LONG_ENOUGH_REGEX)
    password: constr(regex=LONG_ENOUGH_REGEX)
