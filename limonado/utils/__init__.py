# -*- coding: utf-8 -*-

import uuid

__all__ = ["generate_uuid", "join_paths"]


def generate_uuid():
    return uuid.uuid4().hex


def join_paths(*paths):
    parts = []
    for path in paths:
        path = path.strip("/")
        if path:
            parts.append("/{}".format(path))

    return "".join(parts)
