# -*- coding: utf-8 -*-

import warnings

from .application import WebAPI
from .cli import run_cli
from .endpoints import Endpoint
from .exceptions import APIError
from .handlers import EndpointHandler
from .settings import get_default_settings
from .validation import validate_request
from .validation import validate_response

__all__ = [
    "APIError",
    "Endpoint",
    "EndpointHandler",
    "WebAPI",
    "get_default_settings",
    "run_cli",
    "validate_request",
    "validate_response",
]

# Make sure that DeprecationWarning always gets printed.
warnings.filterwarnings("always", category=DeprecationWarning, module=__name__)
