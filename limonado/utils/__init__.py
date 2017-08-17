# -*- coding: utf-8 -*-

from collections import Mapping

__all__ = [
    "merge_defaults"
]


def merge_defaults(defaults, destination):
    """Deep merge defaults into destination.

    On collision, values from destination will be kept.

    """
    for key, value in defaults.items():
        if key not in destination:
            destination[key] = value
        elif isinstance(value, Mapping):
            merge_defaults(value, destination[key])
