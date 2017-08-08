# -*- coding: utf-8 -*-

from tornado.gen import Return
from tornado.gen import coroutine

from .handlers import HealthHandler
from .handlers import WelcomeHandler
from .health import Health

__all__ = [
    "Endpoint",
    "RootEndpoint"
]


class Endpoint(object):
    """Base class for Endpoints."""

    version = "1.0"

    health_handler_class = HealthHandler

    def __init__(self, name, context):
        self.name = name
        self.context = context

    @property
    def is_root(self):
        return not self.name

    @property
    def executor(self):
        return self.context.default_executor

    @property
    def handlers(self):
        return []

    @coroutine
    def check_health(self):
        raise Return(Health())


class RootEndpoint(Endpoint):

    @property
    def handlers(self):
        return [
            ("/", WelcomeHandler),
        ]
