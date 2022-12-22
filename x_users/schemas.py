from django.contrib.auth import get_user_model
from ninja import ModelSchema, Schema

User = get_user_model()


# class BaseUser(Schema):
#    username: str
#    email: str
#    first_name: str = None
#    last_name: str = None
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
        model_fields = ("username", "email", "first_name", "last_name")
