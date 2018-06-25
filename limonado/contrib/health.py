# -*- coding: utf-8 -*-

import datetime
import functools
import time

from tornado.gen import coroutine
from tornado.gen import with_timeout
import tornado.util

from ..core.api import API
from ..core.api import APIHandler

_TIMEOUT = datetime.timedelta(seconds=30)

_HEALTH_PARAMS = {
    "additionalProperties": False,
    "type": "object",
    "properties": {
        "failed_status": {
            "type": "integer",
            "minimum": 500,
            "maximum": 599
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
    def get(self):
        params = self.get_params(_HEALTH_PARAMS)
        health = yield self.api.check_health()
        if health["status"] == "failed":
            self.set_status(params.get("failed_status", 200))

        self.write_json(health)
        self.finish()


class BaseHealthAPI(API):
    @property
    def handlers(self):
        return [("", HealthHandler)]

    @property
    def timeout(self):
        return _TIMEOUT

    @property
    def checks(self):
        return {}

    @coroutine
    def check_health(self):
        issues = yield self._get_issues()
        if issues:
            status = "failed"
        else:
            status = "ok"

        return {"status": status, "issues": issues}

    @coroutine
    def _get_issues(self):
        # Run checks in parallel.
        results = yield {
            name: self._run_check(check)
            for name, check in self.checks.items()
        }
        return {
            name: result
            for name, result in results.items() if result is not None
        }

    @coroutine
    def _run_check(self, check):
        future = check()
        if self.timeout is not None:
            future = with_timeout(
                self.timeout, future, quiet_exceptions=(HealthIssue, ))

        try:
            yield future
        except tornado.util.TimeoutError:
            return {"reason": "Check timed out."}
        except HealthIssue as exc:
            return {"reason": str(exc)}


class HealthAPI(BaseHealthAPI):
    def __init__(self, *, timeout=_TIMEOUT, checks=None, **kwargs):
        super().__init__(**kwargs)
        if hasattr(timeout, "total_seconds"):
            self._timeout = timeout
        else:
            self._timeout = datetime.timedelta(seconds=timeout)

        self._checks = {} if checks is None else checks.copy()

    @property
    def timeout(self):
        return self._timeout

    @property
    def checks(self):
        return self._checks

    def add_check(self, name, func, *args, **kwargs):
        self._checks[name] = functools.partial(func, *args, **kwargs)
        return self


class HealthIssue(Exception):
    pass
