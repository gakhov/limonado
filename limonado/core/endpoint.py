# -*- coding: utf-8 -*-

import abc
import weakref

from tornado.escape import json_decode
from tornado.escape import json_encode
from tornado.web import RequestHandler

from ..exceptions import APIError
from ..utils._params import extract_params
from ..validation import validate_request_data

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

    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")
        self.set_header("Api", self.application.name)
        self.set_header("Api-Version", self.application.version)
        self.set_header("Server", self.application.server)

    def initialize(self, endpoint):
        self.endpoint = endpoint

    def get_params(self, schema):
        params = extract_params(self.request.arguments, schema)
        validate_request_data(params, schema)
        return params

    def get_json(self, schema=None):
        if not self.request.body:
            return None

        try:
            json = json_decode(self.request.body.decode("utf-8"))
        except ValueError:
            raise APIError(400, "Malformed JSON")
        else:
            if schema is not None:
                validate_request_data(json, schema)

            return json

    def write_json(self, value):
        self.write(json_encode(value))

    def write_error(self, status_code, **kwargs):
        self.clear()
        self.set_status(status_code)
        error = {"code": status_code, "message": self._reason}
        exception = kwargs["exc_info"][1]
        if isinstance(exception, APIError):
            error["error"] = {"message": exception.message}
            if exception.details:
                error["error"].update(exception.details)

        self.write_json(error)
