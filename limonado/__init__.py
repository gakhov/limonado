# -*- coding: utf-8 -*-

from .api import WebAPI
from .exceptions import APIError
from .settings import get_default_settings

__all__ = [
    "APIError",
    "WebAPI",
    "get_default_settings"
]
