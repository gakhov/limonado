# -*- coding: utf-8 -*-

import warnings

from .application import WebAPI
from .endpoints import Endpoint
from .exceptions import APIError
from .handlers import EndpointHandler
from .settings import get_default_settings

__all__ = [
    "APIError",
    "Endpoint",
    "EndpointHandler",
    "WebAPI",
    "get_default_settings"
]

# Make sure that DeprecationWarning always gets printed.
warnings.filterwarnings("always", category=DeprecationWarning, module=__name__)
