from api_setup import api
from django.contrib.auth import get_user_model

from db.models import user

User = get_user_model()


@api.get("users/")
def user_list(request):
    return "HEllo!"
