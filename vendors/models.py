from django.db import models
from django.utils.translation import gettext_lazy as _

from db.models import AutoGeneratedSlugModel


class Vendor(AutoGeneratedSlugModel):
    name = models.CharField(
        _("manufacturer name"),
        max_length=150,
        unique=True,
        help_text=_("required, max_len: 150"),
    )
    description = models.TextField(
        _("product vendor brief info"),
        max_length=2000,
        blank=True,
        null=True,
        help_text=_("optional, max_len: 2000"),
    )