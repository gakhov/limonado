# -*- coding: utf-8 -*-

from copy import deepcopy

import jsonschema
from tornado.concurrent import futures

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

    def add_endpoints(self, endpoint_specs):
        for spec in endpoint_specs:
            try:
                endpoint_class, endpoint_kwargs = spec
            except ValueError:
                endpoint_class, endpoint_kwargs = spec, {}

            self.add_endpoint(endpoint_class, endpoint_kwargs=endpoint_kwargs)

        return self

    def get_application(self, enable=None):
        self._validate_settings()
        handlers = self._get_endpoint_handlers(enable)
        return Application(self.settings, handlers=handlers)

    def _create_context(self):
        executor = futures.ThreadPoolExecutor()
        return self.context_class(self.settings, executor, **self.objects)

    def _get_endpoint_handlers(self, enable):
        handlers = []
        context = self._create_context()
        for name, (endpoint_class, endpoint_kwargs) in self._endpoints.items():
            if enable is None or name in enable:
                endpoint = endpoint_class(context, **endpoint_kwargs)
                handlers.extend(
                    _build_versioned_handlers(self.settings["version"],
                                              endpoint))

        return handlers

    def _validate_settings(self):
        try:
            jsonschema.validate(self.settings, schemas.SETTINGS)
        except jsonschema.ValidationError as error:
            raise ValueError(error)


def _build_versioned_handlers(version, endpoint):
    handlers = []
    default_handler_kwargs = {"endpoint": endpoint}

    def make_path(path):
        real_path = path.lstrip("/").replace("{name}", endpoint.name)
        return "/v{version}/{path}".format(version=version, path=real_path)

    def add_handlers(specs):
        for handler in specs:
            try:
                path, handler_class, handler_kwargs = handler
            except ValueError:
                path, handler_class = handler
                handler_kwargs = {}

            handler_kwargs.update(default_handler_kwargs)
            handlers.append((make_path(path), handler_class, handler_kwargs))

    add_handlers(endpoint.handlers)
    for addon in endpoint.iter_addons():
        add_handlers(addon.handlers)

    return handlers
