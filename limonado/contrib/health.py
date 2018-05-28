# -*- coding: utf-8 -*-

import collections
from traceback import format_exception

from tornado.gen import coroutine

from ..core.endpoint import EndpointAddon
from ..core.endpoint import EndpointHandler
from ..validation import validate_response

_Error = collections.namedtuple("_Error", "source reason exception")

_HEALTH_SCHEMA = {
    "additionalProperties": False,
    "type": "object",
    "properties": {
        "ok": {
            "type": "boolean"
        },
        "ok_as_string": {
            "type": "string",
            "enum": [
                "yes",
                "no"
            ]
        },
        "errors": {
            "type": "array",
            "items": {
                "additionalProperties": False,
                "properties": {
                    "source": {
                        "type": ["null", "string"],
                        "minLength": 1
                    },
                    "reason": {
                        "type": ["null", "string"],
                        "minLength": 1
                    },
                    "exception": {
                        "type": ["null", "string"],
                        "minLength": 1
                    }
                },
                "required": [
                    "source",
                    "reason",
                    "exception"
                ]
            }
        }
    },
    "required": [
        "ok",
        "ok_as_string",
        "errors"
    ]
}


class HealthHandler(EndpointHandler):
    response_schema = _HEALTH_SCHEMA

    def initialize(self, endpoint, addon):
        super().initialize(endpoint)
        self._addon = addon

    @coroutine
    def head(self):
        status = yield self._addon.check_health()
        if not status.ok:
            self.set_status(self._addon.unhealthy_status)
        else:
            self.set_status(200)

        self.finish()

    @validate_response(response_schema)
    @coroutine
    def get(self):
        status = yield self._addon.check_health()
        if not status.ok:
            self.set_status(self._addon.unhealthy_status)

        return status.as_json_data()


class HealthAddon(EndpointAddon):
    unhealthy_status = 503

    def __init__(self,
                 endpoint,
                 path="{name}/_health",
                 handler_class=HealthHandler,
                 callback=None):
        super().__init__(endpoint)
        self._path = path
        self._handler_class = handler_class
        self._callback = callback

    @property
    def handlers(self):
        return [
            (self._path, self._handler_class, dict(addon=self))
        ]

    @coroutine
    def check_health(self):
        if self._callback is not None:
            status = yield self._callback(self)
            return status

        return HealthStatus()


class HealthStatus:
    def __init__(self):
        self._errors = []

    @property
    def ok(self):
        return not self._errors

    def as_json_data(self):
        return {
            "ok": self.ok,
            "ok_as_string": "yes" if self.ok else "no",
            "errors": [{
                "source": error.source,
                "reason": error.reason,
                "exception": error.exception,
            } for error in self._errors]
        }

    def add_error(self, source, reason=None):
        self._errors.append(_Error(source, reason, None))
        return self

    def add_exception(self, exc, source=None, reason="exception"):
        tb = "".join(format_exception(type(exc), exc, exc.__traceback__))
        self._errors.append(_Error(source, reason, tb))
        return self
