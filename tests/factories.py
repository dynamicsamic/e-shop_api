import random

import factory
from django.contrib.auth import get_user_model
from faker import Faker

from customers.models import Customer
from vendors.models import Vendor

User = get_user_model()
fake = Faker()

USER_NUM = 10


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda i: f"user{i}")
    email = factory.LazyAttribute(lambda user: f"{user.username}@hello.py")
    first_name = factory.Sequence(lambda _: fake.first_name())
    last_name = factory.Sequence(lambda _: fake.last_name())
    password = "hello"
    is_active = factory.Sequence(
        lambda _: bool(*random.choices((1, 0), weights=(0.6, 0.4)))
    )


class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer

    user = factory.Iterator(User.objects.all())
    status = factory.Sequence(
        lambda _: random.choice(Customer.CustomerStatus.values)
    )
    phone_number = factory.Sequence(
        lambda _: str(fake.pyint(min_value=89000000000, max_value=89999999999))
    )


class VendorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Vendor

    name = factory.Sequence(lambda i: f"Vendor {i}")
    description = factory.Sequence(lambda _: fake.text())
