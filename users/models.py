import logging
from typing import Any, Dict, Literal, Mapping, Tuple

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _

from customers.models import Customer

logger = logging.getLogger(__name__)


class CustomUserManager(UserManager):
    def create_user(self, *args, **kwargs):
        create_customer = kwargs.pop("create_customer", None)
        user = super().create_user(*args, **kwargs)
        if create_customer:
            Customer.objects.create(user=user)
        return user


class User(AbstractUser):
    email = models.EmailField(_("email adress"), unique=True)
    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    objects = CustomUserManager()
