# -*- coding: utf-8 -*-

from collections import namedtuple
from traceback import format_exception

__all__ = ["HealthStatus"]

_Error = namedtuple("_Error", "source reason exception")


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
