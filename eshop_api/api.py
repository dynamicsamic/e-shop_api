from ninja import NinjaAPI

from customers.api import router as custmers_router
from x_users.api import router as users_router

api = NinjaAPI()

api.add_router("/users/", users_router)
api.add_router("/customers/", custmers_router)

from django.urls import reverse_lazy


@api.get("/")
def index(request):
    from django.urls import reverse_lazy

    print(reverse_lazy("api-1.0.0:user_create"))
    return "hello"
