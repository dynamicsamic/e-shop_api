from ninja import NinjaAPI

from customers.api import router as custmers_router

api = NinjaAPI()

api.add_router("/customers/", custmers_router)
