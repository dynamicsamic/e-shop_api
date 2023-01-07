from datetime import datetime

from django.contrib.auth import get_user_model
from ninja import Field, ModelSchema, Schema
from pydantic import constr

from utils import EMAIL_REGEX, LONG_ENOUGH_REGEX
from x_users.schemas import UserOut

from .models import Customer


class CustomerOut(ModelSchema):
    id: int
    username: str = Field(..., alias="user.username")
    email: str = Field(..., alias="user.email")
    first_name: str = Field("", alias="user.first_name")
    last_name: str = Field("", alias="user.last_name")
    is_staff: bool = Field(False, alias="user.is_staff")

    class Config:
        model = Customer
        model_fields = (
            "status",
            "phone_number",
            "created_at",
            "updated_at",
        )


class CustomerCreate(Schema):
    username: constr(regex=LONG_ENOUGH_REGEX)
    email: constr(regex=EMAIL_REGEX)
    password: constr(regex=LONG_ENOUGH_REGEX)
    first_name: str = ""
    last_name: str = ""
    is_active: bool = False
    is_staff: bool = False
    phone_number: str = Field("", min_length=10, max_length=11)
    status: Customer.CustomerStatus = Customer.CustomerStatus.CREATED


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
