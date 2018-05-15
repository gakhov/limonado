# -*- coding: utf-8 -*-

__all__ = ["Endpoint"]


class Endpoint(object):
    """Base class for Endpoints."""

    name = None

    def __init__(self, context):
        self.context = context

    @property
    def handlers(self):
        return []
