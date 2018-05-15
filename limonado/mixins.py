# -*- coding: utf-8 -*-

import abc

from tornado.gen import coroutine

from .handlers import HealthHandler

__all__ = ["WithHealth"]


class WithHealth(abc.ABC):
    health_path = "/{name}/_health"
    health_handler_class = HealthHandler

    @property
    def handlers(self):
        # Mixins must be used in conjunction with endpoints. Here, we
        # get the base endpoint's list of handlers.
        handlers = super().handlers
        handlers.append((self.health_path, self.health_handler_class))
        return handlers

    @abc.abstractmethod
    @coroutine
    def check_health(self):
        pass
