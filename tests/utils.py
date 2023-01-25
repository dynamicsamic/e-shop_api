from typing import Callable

from ninja import Router


def get_ninja_view_from_router(router: Router, path: str) -> Callable:
    """
    Get ninja view from a given path and router.
    Only works with views that utilize only
    one operation, e.g. `get` or `post`, not both.
    """
    path_operations = router.path_operations.get(path).operations[0]
    return path_operations.view_func


def get_ninja_view_from_router_paginated(
    router: Router, path: str
) -> Callable:
    """
    Get ninja view from a given path and router.
    Only works with views that utilize only
    one operation, e.g. `get` or `post`, not both.

    Because view gets decorated by RouterPaginated,
    we need to get the original view from __closure__ attr.
    """
    path_operations = router.path_operations.get(path).operations[0]
    decorated_view = path_operations.view_func
    return decorated_view.__closure__[0].cell_contents
