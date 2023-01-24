from ninja import ModelSchema

from .models import Vendor


class VendorOut(ModelSchema):
    class Config:
        model = Vendor
        model_fields = "__all__"
