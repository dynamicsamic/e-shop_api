from django.test import TestCase

from tests.factories import UserFactory

USER_NUM = 10


class UserTestCase(TestCase):
    def setUp(self):
        self.users = UserFactory.create_batch(USER_NUM)
        for user in self.users:
            user.set_password(user.password)
            user.save(update_fields=("password",))

    def test_user_objects_have_custom_manager(self):
        from x_users.models import CustomUserManager

        self.assertTrue(
            all(
                isinstance(user._meta.model.objects, CustomUserManager)
                for user in self.users
            )
        )

    def test_can_create_customer_along_with_user(self):
        from django.contrib.auth import get_user_model

        from customers.models import Customer

        User = get_user_model()
        valid_data = {
            "username": "user000",
            "email": "user000@hello.py",
            "password": "hello",
            "create_customer": True,
        }
        customer_num_initial = Customer.objects.count()
        User.objects.create_user(**valid_data)
        self.assertEqual(Customer.objects.count(), customer_num_initial + 1)
