import datetime as dt
from typing import Dict

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def updated_at() -> Dict[str, dt.datetime]:
    """Return current time in current timezone.
    Used in update queries.
    """
    return {"updated_at": dt.datetime.now(timezone.get_current_timezone())}
