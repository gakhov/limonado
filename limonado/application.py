# -*- coding: utf-8 -*-

from copy import deepcopy

from tornado.concurrent import futures
import tornado.web

from .context import Context
from .endpoints import RootEndpoint
from .handlers import DeprecatedHandler
from .settings import get_default_settings
from .utils import merge_defaults

__all__ = [
    "WebAPI",
    "Application"
]


class WebAPI(object):

    def __init__(self, settings=None, context=None, context_class=Context,
                 **tornado_settings):
        if settings is None:
            self.settings = {}
        else:
            self.settings = deepcopy(settings)

        merge_defaults(get_default_settings(), self.settings)
        self.tornado_settings = tornado_settings
        if context is None:
            self.context = {}
        else:
            self.context = deepcopy(context)

        self.context_class = context_class
        self._endpoints = {
            "": (RootEndpoint, {})
        }

    @property
    def endpoint_names(self):
        return frozenset(self._endpoints)

    def set_root_endpoint(self, endpoint_class, **endpoint_kwargs):
        self._endpoints[""] = (endpoint_class, endpoint_kwargs)
        return self

    def add_endpoint(self, name, endpoint_class, **endpoint_kwargs):
        if not name:
            raise ValueError("endpoint name must not be None nor empty")

        if name in self._endpoints:
            raise ValueError("duplicate endpoint name: {}".format(name))

        self._endpoints[name] = (endpoint_class, endpoint_kwargs)
        return self

    def add_endpoints(self, endpoint_specs):
        for spec in endpoint_specs:
            try:
                name, endpoint_class, endpoint_kwargs = spec
            except ValueError:
                name, endpoint_class = spec
                endpoint_kwargs = {}

            self.add_endpoint(name, endpoint_class, **endpoint_kwargs)

        return self

    def get_application(self, enable=None):
        handlers = self.tornado_settings.pop("handlers", [])
        self._add_endpoint_handlers(handlers, enable)
        return Application(self.settings, handlers=handlers,
                           **self.tornado_settings)

    def _create_context(self):
        executors = {name: futures.ThreadPoolExecutor(threads)
                     for name, threads in self.settings["threads"].items()}
        return self.context_class(self.settings, executors, **self.context)

    def _add_endpoint_handlers(self, handlers, enable):
        context = self._create_context()
        for name, (endpoint_class, endpoint_kwargs) in self._endpoints.items():
            if enable is None or name in enable:
                endpoint = endpoint_class(name, context, **endpoint_kwargs)
                handlers.extend(_build_versioned_handlers(
                    endpoint,
                    self.settings["version"],
                    self.settings["deprecated_versions"]))


def _build_versioned_handlers(endpoint, active_version, deprecated_versions):

    def make_path(path, version=active_version):
        if endpoint.is_root:
            fmt = "/v{version}{path}"
        else:
            fmt = "/v{version}/{name}{path}"

        return fmt.format(version=version, name=endpoint.name, path=path)

    versioned_paths = set()
    default_handler_kwargs = {
        "endpoint": endpoint
    }
    handlers = []
    handlers.append((make_path("/_health"), endpoint.health_handler_class,
                     default_handler_kwargs))
    for handler in endpoint.handlers:
        try:
            path, handler_class, handler_kwargs = handler
        except ValueError:
            path, handler_class = handler
            handler_kwargs = {}

        versioned_paths.add(path)
        handler_kwargs.update(default_handler_kwargs)
        handlers.append((make_path(path), handler_class, handler_kwargs))

    for version in deprecated_versions:
        for handler in endpoint.handlers:
            path = handler[0]
            deprecated_path = make_path(path, version=version)
            if deprecated_path not in versioned_paths:
                handlers.append((deprecated_path, DeprecatedHandler,
                                 default_handler_kwargs))

    return handlers


class Application(tornado.web.Application):

    def __init__(self, settings, **tornado_settings):
        super(Application, self).__init__(**tornado_settings)
        self.name = settings["name"]
        self.port = settings["port"]
        self.version = settings["version"]
        self.deprecated_versions = settings["deprecated_versions"]
        self.server = settings["server"]
