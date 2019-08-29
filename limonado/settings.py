# -*- coding: utf-8 -*-

import uuid

from .__about__ import __version__

__all__ = [
    "get_default_settings"
]


def get_default_settings():
    return {
        "name": "Limonado",
        "id": uuid.uuid4().hex[:8],
        "version": "1",
        "server": "Limonado/{}".format(__version__)
    }
