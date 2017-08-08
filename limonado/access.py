# -*- coding: utf-8 -*-

from functools import wraps

from .exceptions import APIError
from .utils import container

__all__ = [
    "authenticated",
    "authorized"
]


def authenticated():
    """Check if user is registered and can be authenticated."""
    @container
    def _authenticate(rh_method):

        @wraps(rh_method)
        def _wrapper(self, *args, **kwargs):
            if self.current_user is None:
                raise APIError(401, "Not Authenticated")

            return rh_method(self, *args, **kwargs)

        return _wrapper

    return _authenticate


def authorized(*scopes):

    @container
    def _check(rh_method):

        @wraps(rh_method)
        def _wrapper(self, *args, **kwargs):
            if self.current_user is None:
                raise APIError(401, "Not Authenticated")

            if (not self.current_user.is_superuser and
                    not any(scope in self.current_user.scopes
                            for scope in scopes)):
                raise APIError(403, "Access Denied")

            return rh_method(self, *args, **kwargs)

        return _wrapper

    return _check
