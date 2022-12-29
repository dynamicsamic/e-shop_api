from django.contrib.auth import get_user_model
from ninja import ModelSchema, Schema
from pydantic import constr

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
EMAIL_REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
LONG_ENOUGH_REGEX = r"[A-Za-z0-9._%+-]{4}"


class UserIn(Schema):
    username: constr(regex=LONG_ENOUGH_REGEX)
    email: constr(regex=EMAIL_REGEX)
    password: constr(regex=LONG_ENOUGH_REGEX)
    # first_name: str = ""
    # last_name: str = ""


class UserUpdate(Schema):
    email: constr(regex=EMAIL_REGEX) = ""
    first_name: str = ""
    last_name: str = ""


class ErrorMessage(Schema):
    error_message: str
