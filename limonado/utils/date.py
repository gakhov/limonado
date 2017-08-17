# -*- coding: utf-8 -*-

from datetime import timedelta

from dateutil.parser import parse as parse_date

__all__ = [
    "parse_date",
    "parse_duration"
]

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
