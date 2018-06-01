# -*- coding: utf-8 -*-

from tornado.gen import coroutine

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


class HealthHandler(EndpointHandler):
    def initialize(self, endpoint, addon):
        super().initialize(endpoint)
        self._addon = addon

    @coroutine
    def head(self):
        status = yield self._check_health()
        if not status["ok"]:
            self.set_status(self._addon.unhealthy_status)

        self.finish()

    @coroutine
    def get(self):
        status = yield self._check_health()
        if not status["ok"]:
            self.set_status(self._addon.unhealthy_status)

        self.write_json(status)
        self.finish()

    @coroutine
    def _check_health(self):
        params = self.get_params(_HEALTH_PARAMS)
        errors = yield self._addon.check_health(include=params.get("check"))
        ok = not errors
        return {
            "ok": ok,
            "ok_as_string": "true" if ok else "false",
            "errors": errors
        }


class HealthAddon(EndpointAddon):
    unhealthy_status = 503

    def __init__(self,
                 endpoint,
                 path="{name}/_health",
                 handler_class=HealthHandler,
                 checks=None):
        super().__init__(endpoint)
        self._path = path
        self._handler_class = handler_class
        self._checks = dict(checks) if checks is not None else {}

    @property
    def handlers(self):
        return [
            (self._path, self._handler_class, dict(addon=self))
        ]

    @coroutine
    def check_health(self, include=None):
        errors = {}
        for name, check in self._checks.items():
            if include is None or name in include:
                try:
                    yield check(self)
                except HealthError as exc:
                    errors[name] = exc.error

        return errors


class HealthError(Exception):
    def __init__(self, error):
        self._error = error

    @property
    def error(self):
        return self._error
