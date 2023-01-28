from ninja import ModelSchema, Schema
from pydantic import Field

from .models import Vendor


class VendorOut(ModelSchema):
    class Config:
        model = Vendor
        model_fields = "__all__"


class VendorIn(Schema):
    name: str = Field(..., min_length=3, max_length=150)
    description: str
