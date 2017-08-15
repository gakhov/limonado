# -*- coding: utf-8 -*-

import multiprocessing

from .__about__ import __version__

__all__ = [
    "get_default_settings"
]


def get_default_settings():
    return {
        "name": "Limonado",
        "version": "1.0",
        "port": "8000",
        "version": "1.0",
        "deprecated_versions": [],
        "server": "Limonado/{}".format(__version__),
        "threads": {
            "default": multiprocessing.cpu_count()
        }
    }
