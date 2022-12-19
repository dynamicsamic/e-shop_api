import datetime as dt
import logging
from typing import Any, Dict, Literal, Mapping, Tuple

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _

from .utils import TimeStampModel

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


class UserRoleManager(models.Manager):
    def get_queryset(self) -> "QuerySet[AbstractUserRole]":
        """Fetch user data when querying for Role object."""
        return super().get_queryset().select_related("user")


class AbstractUserRole(models.Model):
    """Abstract class for implementing user roles,
    e.g. customer, moderator, admin, etc."""

    user = None

    objects = UserRoleManager()

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.username

    @property
    def username(self) -> str:
        return self.user.get_username()

    @property
    def email(self) -> str:
        return self.user.email

    @email.setter
    def email(self, new_email: str) -> None:
        self.user.email = new_email
        self.user.save(update_fields=("email",))

    @property
    def first_name(self) -> str:
        return self.user.first_name

    @first_name.setter
    def first_name(self, new_first_name: str) -> None:
        self.user.first_name = new_first_name
        self.user.save(update_fields=("first_name",))

    @property
    def last_name(self) -> str:
        return self.user.last_name

    @last_name.setter
    def last_name(self, new_last_name: str) -> None:
        self.user.last_name = new_last_name
        self.user.save(update_fields=("last_name",))

    @property
    def full_name(self) -> str:
        return self.user.get_full_name()

    @property
    def last_login(self) -> dt.datetime or None:
        return self.user.last_login

    @property
    def date_joined(self) -> dt.datetime:
        return self.user.date_joined

    @property
    def is_active(self) -> bool:
        return self.user.is_active

    @property
    def is_anonymous(self) -> bool:
        return self.user.is_anonymous

    @property
    def is_authenticated(self) -> bool:
        return self.user.is_authenticated

    @property
    def groups(self):
        return self.user.groups


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


class Moderator(AbstractUserRole):
    """Needs fixing. Meanwhile leave it abstract."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="moderator",
    )

    class Meta:
        abstract = True
