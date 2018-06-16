# -*- coding: utf-8 -*-

from itertools import chain

from .. import utils
from .handlers import RequestHandler

__all__ = ["API", "APIHandler"]


class APIMeta(type):
    def __subclasscheck__(cls, subclass):
        if issubclass(subclass, APIDecorator):
            return True

        return super().__subclasscheck__(subclass)

    def __instancecheck__(self, other):
        if isinstance(other, APIDecorator):
            return True

        return super().__instancecheck__(other)


class API(metaclass=APIMeta):
    """Base class for APIs."""

    def __init__(self):
        self._subapis = _APIContainer()
        self._extra_handlers = []

    @property
    def handlers(self):
        return []

    def add_handler(self, path, handler_class):
        self._extra_handlers.append((path, handler_class))
        return self

    def add_subapi(self, path, api):
        self._subapis.add(path, api)
        return self

    def iter_subapis(self, *, max_depth=0):
        return self._subapis.iter(max_depth=max_depth)

    def iter_handlers(self, base_path=""):
        handlers = chain.from_iterable([self.handlers, self._extra_handlers])
        for path, handler_class in handlers:
            full_path = utils.join_paths(base_path, path)
            init_dict = {"api": self}
            yield full_path, handler_class, init_dict

        stack = list(self._subapis.iter(max_depth=0))
        while stack:
            subapi = stack.pop()
            for path, handler_class, init_dict in subapi.iter_handlers():
                full_path = utils.join_paths(base_path, subapi.path, path)
                yield full_path, handler_class, init_dict

            stack.extend(subapi.iter_subapis(max_depth=0))

    def initialize(self):
        pass


class APIDecorator:
    def __init__(self, api):
        self._api = api

    def __getattr__(self, attr):
        return getattr(self._api, attr)


class APIHandler(RequestHandler):
    """Base class for endpoint handlers."""

    def initialize(self, api):
        self.api = api


class _SubAPI(APIDecorator):
    def __init__(self, api, path):
        super().__init__(api)
        self._path = path

    @property
    def path(self):
        return self._path


class _APIContainer:
    def __init__(self):
        self._apis = []

    def add(self, path, api):
        self._apis.append(_SubAPI(api, path))

    def iter(self, *, max_depth=0):
        stack = [(api, 0) for api in self._apis]
        while stack:
            api, depth = stack.pop()
            yield api
            if max_depth is None or depth < max_depth:
                stack.extend(
                    (subapi, depth + 1) for subapi in api.iter_subapis())
