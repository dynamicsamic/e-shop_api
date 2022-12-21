import random

import factory
from django.contrib.auth import get_user_model
from faker import Faker

from customers.models import Customer

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


class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer

    user = factory.Iterator(User.objects.all())
    status = factory.Sequence(
        lambda _: random.choice(Customer.CustomerStatus.values)
    )
    phone_number = factory.Sequence(lambda _: fake.phone_number())
