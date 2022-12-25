from django.contrib.auth import get_user_model
from ninja import ModelSchema, Schema

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


class UserIn(ModelSchema):
    class Config:
        model = User
        model_fields = (
            "username",
            "password",
            "email",
        )


class UserIns(Schema):
    username: str
    email: str
    password: str
    # first_name: str = ""
    # last_name: str = ""


class Message(Schema):
    message: str
