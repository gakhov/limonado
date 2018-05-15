# -*- coding: utf-8 -*-

from copy import deepcopy

import jsonschema
from tornado.concurrent import futures
import tornado.web

from .context import Context
from .settings import get_default_settings
from .utils import merge_defaults
from .validation import schemas

__all__ = ["Application", "WebAPI"]


class WebAPI(object):
    def __init__(self,
                 settings=None,
                 context_class=Context,
                 **tornado_settings):
        if settings is None:
            self.settings = {}
        else:
            self.settings = deepcopy(settings)

        merge_defaults(get_default_settings(), self.settings)
        self.objects = {}
        self.context_class = context_class
        self.tornado_settings = tornado_settings
        self._endpoints = {}

    @property
    def endpoint_names(self):
        return frozenset(self._endpoints)

    def add_endpoint(self, endpoint_class, **endpoint_kwargs):
        name = endpoint_class.name
        if not name:
            raise ValueError("endpoint name must not be None nor empty")

        if name in self._endpoints:
            raise ValueError("duplicate endpoint name: {}".format(name))

        self._endpoints[name] = (endpoint_class, endpoint_kwargs)
        return self

    def add_endpoints(self, endpoint_specs):
        for spec in endpoint_specs:
            try:
                endpoint_class, endpoint_kwargs = spec
            except ValueError:
                endpoint_class, endpoint_kwargs = spec, {}

            self.add_endpoint(endpoint_class, **endpoint_kwargs)

        return self

    def get_application(self, enable=None):
        self._validate_settings()
        handlers = self.tornado_settings.pop("handlers", [])
        self._add_endpoint_handlers(handlers, enable)
        return Application(
            self.settings, handlers=handlers, **self.tornado_settings)

    def _create_context(self):
        executors = {
            name: futures.ThreadPoolExecutor(threads)
            for name, threads in self.settings["threads"].items()
        }
        return self.context_class(self.settings, executors, **self.objects)

    def _add_endpoint_handlers(self, handlers, enable):
        context = self._create_context()
        for name, (endpoint_class, endpoint_kwargs) in self._endpoints.items():
            if enable is None or name in enable:
                endpoint = endpoint_class(context, **endpoint_kwargs)
                handlers.extend(
                    _build_versioned_handlers(self.settings["version"],
                                              endpoint))

    def _validate_settings(self):
        try:
            jsonschema.validate(self.settings, schemas.SETTINGS)
        except jsonschema.ValidationError as error:
            raise ValueError(error)


def _build_versioned_handlers(version, endpoint):
    def make_path(path):
        real_path = path.lstrip("/").replace("{name}", endpoint.name)
        return "/v{version}/{path}".format(version=version, path=real_path)

    default_handler_kwargs = {"endpoint": endpoint}
    handlers = []
    handlers.append((make_path("/{name}/_health"),
                     endpoint.health_handler_class, default_handler_kwargs))
    for handler in endpoint.handlers:
        try:
            path, handler_class, handler_kwargs = handler
        except ValueError:
            path, handler_class = handler
            handler_kwargs = {}

        handler_kwargs.update(default_handler_kwargs)
        handlers.append((make_path(path), handler_class, handler_kwargs))

    return handlers


class Application(tornado.web.Application):
    def __init__(self, settings, **tornado_settings):
        super(Application, self).__init__(**tornado_settings)
        self.name = settings["name"]
        self.id = settings["id"]
        self.version = settings["version"]
        self.server = settings["server"]
