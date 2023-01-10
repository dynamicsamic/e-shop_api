from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from db.models import AbstractUserRole, TimeStampModel


class Customer(AbstractUserRole, TimeStampModel):
    class CustomerStatus(models.TextChoices):
        CREATED = "created"
        ACTIVATED = "activated"
        FROZEN = "frozen"
        ARCHIVED = "archived"

    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="customer",
    )
    status = models.CharField(
        _("Customer status"),
        max_length=20,
        help_text=_("required, default: created"),
        choices=CustomerStatus.choices,
        default=CustomerStatus.CREATED,
    )
    phone_number = models.CharField(
        _("Customer phone number"),
        help_text=_("optional, max_len: 15"),
        max_length=15,
        blank=True,
        null=True,
    )
