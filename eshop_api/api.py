from ninja import NinjaAPI

from accounts.api import router as users_router
from customers.api import router as custmers_router

api = NinjaAPI()

api.add_router("/users/", users_router)
api.add_router("/customers/", custmers_router)
