from django.db import IntegrityError

EMAIL_REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
LONG_ENOUGH_REGEX = r"[A-Za-z0-9._%+-]{4}"


def trim_attr_name_from_integrity_error(error: IntegrityError) -> str:
    """Extract the last part from IntegrityError traceback
    which points to non-unique attr.

    Example.
    `IntegrityError('UNIQUE constraint failed: x_users_user.email')`
    results in `email`."""
    import re

    rexp = ".+\.([a-z]+$)"
    if result := re.search(rexp, str(error)):
        return result.group(1)
    return ""
