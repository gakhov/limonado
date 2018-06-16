# -*- coding: utf-8 -*-

import functools
import time
import weakref

from tornado.gen import coroutine

from ..core.api import API
from ..core.api import APIHandler

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


class HealthHandler(APIHandler):
    @coroutine
    def head(self):
        health = yield self.check_health()
        if health["status"] == "unhealthy":
            self.set_status(self.api.unhealthy_status)

        self.finish()

    @coroutine
    def get(self):
        health = yield self.check_health()
        if health["status"] == "unhealthy":
            self.set_status(self.api.unhealthy_status)

        self.write_json(health)
        self.finish()

    @coroutine
    def check_health(self):
        params = self.get_params(_HEALTH_PARAMS)
        issues = yield self.api.check_health(include=params.get("check"))
        status = "unhealthy" if issues else "healthy"
        return {"status": status, "issues": issues}


class HealthAPI(API):
    def __init__(self,
                 parent=None,
                 prefix="/health",
                 handler_class=HealthHandler,
                 unhealthy_status=503,
                 checks=None,
                 **kwargs):
        super().__init__(**kwargs)
        if parent is None:
            self._parent = None
        else:
            self._parent = weakref.proxy(parent)

        self._prefix = prefix
        self._handler_class = handler_class
        self._unhealthy_status = unhealthy_status
        if checks is None:
            self._checks = {}
        elif callable(checks):
            self._checks = checks(self)
        else:
            self._checks = dict(checks)

    @property
    def parent(self):
        return self._parent

    @property
    def prefix(self):
        return self._prefix

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
        return [("", self._handler_class)]

    @coroutine
    def check_health(self, include=None):
        issues = {}
        for name, check in self.checks.items():
            if include is None or name in include:
                try:
                    yield check(self)
                except HealthIssue as issue:
                    issues[name] = {
                        "message": issue.message,
                        "details": issue.details
                    }

        return issues


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
