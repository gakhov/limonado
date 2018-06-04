# -*- coding: utf-8 -*-

import functools
import time

from tornado.gen import coroutine

from ..core.endpoint import Endpoint
from ..core.endpoint import EndpointAddon
from ..core.endpoint import EndpointHandler

_HEALTH_PARAMS = {
    "additionalProperties": False,
    "type": "object",
    "properties": {
        "check": {
            "type": "array",
            "itemSeparator": ",",
            "items": {
                "type": "string"
            }
        }
    }
}


def cache_health(ttl):
    if hasattr(ttl, "total_seconds"):
        ttl_seconds = ttl.total_seconds()
    else:
        ttl_seconds = ttl

    def decorate(check):
        health_error = None
        expires = None

        @coroutine
        @functools.wraps(check)
        def wrap(addon):
            nonlocal health_error, expires
            if expires is not None and time.time() <= expires:
                if health_error is not None:
                    raise health_error
            else:
                try:
                    yield check(addon)
                except HealthError as exc:
                    health_error = exc
                    raise
                else:
                    health_error = None
                finally:
                    expires = time.time() + ttl_seconds

        return wrap

    return decorate


class HealthHandler(EndpointHandler):
    def initialize(self, endpoint, addon):
        super().initialize(endpoint)
        self.addon = addon

    @coroutine
    def head(self):
        status = yield self._check_health()
        if not status["ok"]:
            self.set_status(self.addon.unhealthy_status)

        self.finish()

    @coroutine
    def get(self):
        status = yield self._check_health()
        if not status["ok"]:
            self.set_status(self.addon.unhealthy_status)

        self.write_json(status)
        self.finish()

    @coroutine
    def _check_health(self):
        params = self.get_params(_HEALTH_PARAMS)
        errors = yield self.addon.check_health(include=params.get("check"))
        ok = not errors
        return {
            "ok": ok,
            "ok_as_string": "true" if ok else "false",
            "errors": errors
        }


class HealthAddon(EndpointAddon):
    def __init__(self,
                 endpoint,
                 path="{name}/health",
                 handler_class=HealthHandler,
                 unhealthy_status=503,
                 checks=None):
        super().__init__(endpoint)
        self._path = path
        self._handler_class = handler_class
        self._unhealthy_status = unhealthy_status
        self._checks = dict(checks) if checks is not None else {}

    @property
    def path(self):
        return self._path

    @property
    def handler_class(self):
        return self._handler_class

    @property
    def unhealthy_status(self):
        return self._unhealthy_status

    @property
    def checks(self):
        return self._checks

    @property
    def handlers(self):
        return [(self._path, self._handler_class, dict(addon=self))]

    @coroutine
    def check_health(self, include=None):
        errors = {}
        for name, check in self.checks.items():
            if include is None or name in include:
                try:
                    yield check(self.endpoint)
                except HealthError as exc:
                    errors[name] = exc.error

        return errors


class HealthEndpoint(Endpoint):
    name = "health"

    def __init__(self, context, **kwargs):
        super().__init__(context)
        kwargs.setdefault("path", "/{name}")
        kwargs["checks"] = self.checks
        self.add_addon(HealthAddon, addon_kwargs=kwargs)

    @property
    def checks(self):
        return {}


class HealthError(Exception):
    def __init__(self, error):
        self._error = error

    @property
    def error(self):
        return self._error
