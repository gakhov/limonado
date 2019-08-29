# -*- coding: utf-8 -*-

from functools import wraps

from .exceptions import APIError
from .utils.decorators import container

__all__ = ["authenticated", "authorized"]


def authenticated(rh_method):
    """Check if user is registered and can be authenticated."""

    @wraps(rh_method)
    def _wrapper(self, *args, **kwargs):
        if self.current_user is None:
            raise APIError(401, "Not Authenticated")

        return rh_method(self, *args, **kwargs)

    return _wrapper


def authorized(*permissions):
    @container
    def _check(rh_method):
        @wraps(rh_method)
        def _wrapper(self, *args, **kwargs):
            user = self.current_user
            if user is None:
                raise APIError(401, "Not Authenticated")

            if not any(
                    user.has_permission(permission)
                    for permission in permissions):
                raise APIError(403, "Insufficient Permissions")

            return rh_method(self, *args, **kwargs)

        return _wrapper

    return _check
