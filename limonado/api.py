# -*- coding: utf-8 -*-

from copy import deepcopy
import os

import jsonschema
from tornado.concurrent import futures
import tornado.ioloop

from .core.application import Application
from .core.context import Context
from .settings import get_default_settings
from .utils import merge_defaults
from .validation import schemas

__all__ = ["WebAPI"]


class WebAPI:
    def __init__(self, settings=None, objects=None, context_class=Context):
        if settings is None:
            self.settings = {}
        else:
            self.settings = deepcopy(settings)

        merge_defaults(get_default_settings(), self.settings)
        self.objects = objects if objects is not None else {}
        self.context_class = context_class
        self._endpoints = {}

    @property
    def endpoint_names(self):
        return frozenset(self._endpoints)

    def add_endpoint(self, endpoint_class, endpoint_kwargs=None):
        name = endpoint_class.name
        if not name:
            raise ValueError("endpoint name must not be None nor empty")

        if name in self._endpoints:
            raise ValueError("duplicate endpoint name: {}".format(name))

        self._endpoints[name] = (endpoint_class, endpoint_kwargs or {})
        return self

    def add_endpoints(self, endpoints):
        for endpoint in endpoints:
            try:
                endpoint_class, endpoint_kwargs = endpoint
            except ValueError:
                endpoint_class = endpoint
                endpoint_kwargs = {}

            self.add_endpoint(endpoint_class, endpoint_kwargs=endpoint_kwargs)

        return self

    def run(self, port=8000, address="", **kwargs):
        app = self.get_application(**kwargs)
        app.listen(port, address=address)
        tornado.ioloop.IOLoop.current().start()

    def get_application(self, enable=None):
        self._validate_settings()
        endpoints = self._create_endpoints(enable)
        endpoint_handlers = self._get_endpoint_handlers(endpoints)
        return Application(self.settings, handlers=endpoint_handlers)

    def _validate_settings(self):
        try:
            jsonschema.validate(self.settings, schemas.SETTINGS)
        except jsonschema.ValidationError as error:
            raise ValueError(error)

    def _get_api_path(self):
        return "{base_path}/v{version}/".format(
            base_path=self.settings.get("base_path", "").rstrip("/"),
            version=self.settings["version"])

    def _create_endpoints(self, enable):
        endpoints = []
        context = self._create_context()
        for name, (endpoint_class, endpoint_kwargs) in self._endpoints.items():
            if enable is None or name in enable:
                endpoint = endpoint_class(context, **endpoint_kwargs)
                endpoints.append(endpoint)

        return endpoints

    def _create_context(self):
        executor = futures.ThreadPoolExecutor((os.cpu_count() or 1) * 5)
        return self.context_class(self.settings, executor, **self.objects)

    def _get_endpoint_handlers(self, endpoints):
        handlers = []
        api_path = self._get_api_path()
        seen = {}
        for endpoint in endpoints:
            print("Enabling", endpoint.name)
            for handler in _build_endpoint_handlers(endpoint, api_path):
                path = handler[0]
                print("=>", path)
                if path in seen:
                    first_endpoint = seen[path]
                    raise ValueError("duplicate path '{}' in '{}', "
                                     "first found in '{}'".format(
                                         path, endpoint.name,
                                         first_endpoint.name))

                handlers.append(handler)
                seen[path] = endpoint

        return handlers


def _build_endpoint_handlers(endpoint, api_path):
    for handler in _iter_handlers(endpoint):
        try:
            handler_path, handler_class, handler_kwargs = handler
        except ValueError:
            handler_path, handler_class = handler
            handler_kwargs = {}

        handler_kwargs["endpoint"] = endpoint
        path = api_path + handler_path.lstrip("/").replace(
            "{name}", endpoint.name)
        yield path, handler_class, handler_kwargs


def _iter_handlers(endpoint):
    yield from endpoint.handlers
    for addon in endpoint.iter_addons():
        yield from addon.handlers
