# -*- coding: utf-8 -*

from .utils import parse_duration

__all__ = [
    "validate_duration"
]


def validate_duration(instance):
    try:
        parse_duration(instance)
    except ValueError:
        return False
    else:
        return True
