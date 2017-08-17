# -*- coding: utf-8 -*-

from functools import wraps

__all__ = [
    "container"
]


def container(dec):
    """Meta-decorator (for decorating decorators).

    Credits: http://stackoverflow.com/a/1167248/1798683

    """
    @wraps(dec)
    def meta_decorator(func):
        decorator = dec(func)
        decorator.orig_func = func
        return decorator

    return meta_decorator
