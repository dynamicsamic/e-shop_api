from django.db import IntegrityError


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
