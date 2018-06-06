# -*- coding: utf-8 -*-

import os
import uuid

from .__about__ import __version__

__all__ = ["get_default_config"]


def _get_env():
    return os.environ.get("LIMONADO_ENV") or "production"


def get_default_config(env=_get_env()):
    debug = env == "development"
    return {
        "debug": debug,
        "name": "Limonado",
        "id": uuid.uuid4().hex[:8],
        "version": "1",
        "server": "Limonado/{}".format(__version__)
    }
