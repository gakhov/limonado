# -*- coding: utf-8 -*-

from tornado.gen import coroutine

from .handlers import HealthHandler
from .health import HealthStatus

__all__ = ["WithHealth"]


class WithHealth:
    health_path = "{name}/_health"
    health_handler_class = HealthHandler

    @property
    def handlers(self):
        handlers = super().handlers
        handlers.append((self.health_path, self.health_handler_class))
        return handlers

    @coroutine
    def check_health(self):
        return HealthStatus()
