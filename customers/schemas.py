from django.contrib.auth import get_user_model
from ninja import Field, ModelSchema, Schema
from pydantic import constr

from .models import Customer


class CustomerOut(Schema):
    username: str
    user_email: str = Field(None, alias="user.email")


"""
EMAIL_REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
LONG_ENOUGH_REGEX = r"[A-Za-z0-9._%+-]{4}"


class UserIn(Schema):
    username: constr(regex=LONG_ENOUGH_REGEX)
    email: constr(regex=EMAIL_REGEX)
    password: constr(regex=LONG_ENOUGH_REGEX)
    create_customer: bool = False
    # first_name: str = ""
    # last_name: str = ""


class UserUpdate(Schema):
    email: constr(regex=EMAIL_REGEX) = ""
    first_name: str = ""
    last_name: str = ""



"""
