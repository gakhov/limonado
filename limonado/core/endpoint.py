# -*- coding: utf-8 -*-

import abc
import weakref

from .handlers import RequestHandler

__all__ = ["Endpoint", "EndpointAddon", "EndpointHandler"]


class Endpoint:
    """Base class for Endpoints."""
    name = None
    addons = []

    def __init__(self, context):
        self._context = context
        self._addon_map = {}
        for spec in self.addons:
            try:
                addon_class, kwargs = spec
            except TypeError:
                addon_class = spec
                kwargs = {}

            self.add_addon(addon_class, addon_kwargs=kwargs)

    @property
    def context(self):
        return self._context

    @property
    def handlers(self):
        return []

    def add_addon(self, addon_class, addon_kwargs=None):
        addon = addon_class(self, **(addon_kwargs or {}))
        self._addon_map[addon_class] = addon

    def get_addon(self, name):
        return self._addon_map.get(name)

    def iter_addons(self):
        return (addon for addon in self._addon_map.values())


class EndpointAddon(abc.ABC):
    """Base class for endpoint addons."""

    def __init__(self, endpoint):
        self._endpoint = weakref.proxy(endpoint)

    @property
    def endpoint(self):
        return self._endpoint

    @property
    def context(self):
        return self._endpoint.context

    @abc.abstractproperty
    def handlers(self):
        pass


class EndpointHandler(RequestHandler):
    """Base class for endpoint handlers."""

    def initialize(self, endpoint):
        self.endpoint = endpoint
