from django.core.management import call_command
from django.core.management.base import BaseCommand

from ... import factories

USER_NUM = VENDOR_NUM = 10


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command("makemigrations")
        call_command("migrate")
        users = factories.UserFactory.create_batch(USER_NUM)
        for user in users:
            user.set_password(user.password)
            user.save(update_fields=("password",))
        customers = factories.CustomerFactory.create_batch(USER_NUM)
        vendors = factories.VendorFactory.create_batch(VENDOR_NUM)
