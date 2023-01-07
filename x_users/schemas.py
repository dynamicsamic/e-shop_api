from django.contrib.auth import get_user_model
from ninja import ModelSchema, Schema
from pydantic import constr

from utils import EMAIL_REGEX, LONG_ENOUGH_REGEX

User = get_user_model()
#

# class UserOut(BaseUser):
#    id: int
#    is_active: bool
#    is_staff: bool


class UserOut(ModelSchema):
    class Config:
        model = User
        model_exclude = (
            "password",
            "groups",
            "last_login",
            "user_permissions",
        )


# class UserInffdfd(ModelSchema):
#    class Config:
#        model = User
#        model_fields = (
#            "username",
#            "password",
#            "email",
#        )
#
#    print("foooo")    return item


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


class ErrorMessage(Schema):
    error_message: str
