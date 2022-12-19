from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Customer

User = get_user_model()


class UserCustomerTestCase(TestCase):
    def test_create_customer_along_with_user(self):
        users_count = User.objects.count()
        customer_count = Customer.objects.count()
        valid_data = {"username": "user1", "email": "user1@hello.py"}
        User.objects.create_user(create_customer=True, **valid_data)
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertEqual(Customer.objects.count(), customer_count + 1)
