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
        issue = None
        expiration_time = None

        @coroutine
        @functools.wraps(check)
        def wrap(*args, **kwargs):
            nonlocal issue, expiration_time
            if expiration_time is not None and time.time() <= expiration_time:
                if issue is not None:
                    raise issue
            else:
                try:
                    yield check(*args, **kwargs)
                except HealthIssue as exc:
                    issue = exc
                    raise
                else:
                    issue = None
                finally:
                    expiration_time = time.time() + ttl_seconds

        return wrap

    return decorate


class HealthHandler(EndpointHandler):
    def initialize(self, endpoint, addon):
        super().initialize(endpoint)
        self.addon = addon

    @coroutine
    def head(self):
        health = yield self.check_health()
        if health["status"] == "unhealthy":
            self.set_status(self.addon.unhealthy_status)

        self.finish()

    @coroutine
    def get(self):
        health = yield self.check_health()
        if health["status"] == "unhealthy":
            self.set_status(self.addon.unhealthy_status)

        self.write_json(health)
        self.finish()

    @coroutine
    def check_health(self):
        params = self.get_params(_HEALTH_PARAMS)
        issues = yield self.addon.check_health(include=params.get("check"))
        status = "unhealthy" if issues else "healthy"
        return {"status": status, "issues": issues}


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
        issues = {}
        for name, check in self.checks.items():
            if include is None or name in include:
                try:
                    yield check(self.endpoint)
                except HealthIssue as issue:
                    issues[name] = {
                        "message": issue.message,
                        "details": issue.details
                    }

        return issues


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


class HealthIssue(Exception):
    def __init__(self, message, details=None):
        self._message = message
        self._details = {} if details is None else dict(details)

    @property
    def message(self):
        return self._message

    @property
    def details(self):
        return self._details
