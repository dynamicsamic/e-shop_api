from django.http import HttpResponse
from ninja import NinjaAPI
from ninja.errors import ValidationError

from customers.api import router as custmers_router
from vendors.api import router as vendors_router
from x_auth.api import router as auth_router
from x_users.api import router as users_router

api = NinjaAPI()

api.add_router("/users/", users_router)
api.add_router("/customers/", custmers_router)
api.add_router("/auth/", auth_router)
api.add_router("/vendors", vendors_router)
