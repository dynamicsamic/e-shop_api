import datetime as dt
from typing import Dict

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class TimeStampModel(models.Model):
    """Django model with `created_at` and `updated_at` fields."""

    created_at = models.DateTimeField(
        _("object creation time"),
        help_text=_("format: Y-m-d H:M:S"),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _("object last update time"),
        help_text=_("format: Y-m-d H:M:S"),
        auto_now=True,
    )

    class Meta:
        abstract = True


def updated_at() -> Dict[str, dt.datetime]:
    """Return current time in current timezone.
    Used in update queries.
    """
    return {"updated_at": dt.datetime.now(timezone.get_current_timezone())}
