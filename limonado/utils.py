# -*- coding: utf-8 -*-

from collections import Mapping
from datetime import timedelta
from functools import wraps

from dateutil.parser import parse as parse_date

__all__ = [
    "container",
    "merge_defaults",
    "parse_date",
    "parse_duration"
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


def merge_defaults(defaults, destination):
    """Deep merge defaults into destination.

    On collision, values from destination will be kept.

    """
    for key, value in defaults.items():
        if key not in destination:
            destination[key] = value
        elif isinstance(value, Mapping):
            merge_defaults(value, destination[key])


_UNIT_TIMEDELTA_ARGS = (
    ("ms", "milliseconds"),
    ("s", "seconds"),
    ("m", "minutes"),
    ("h", "hours"),
    ("d", "days"),
    ("w", "weeks")
)


def parse_duration(value):
    if isinstance(value, (float, int)):
        return timedelta(seconds=value)

    for unit, arg in _UNIT_TIMEDELTA_ARGS:
        if value.endswith(unit):
            rest = value[:-len(unit)]
            try:
                number = float(rest)
            except TypeError:
                raise ValueError("invalid duration value: {}".format(rest))
            else:
                return timedelta(**{arg: number})

    raise ValueError("invalid duration: {}".format(value))
