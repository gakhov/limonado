# -*- coding: utf-8 -*-

from collections import namedtuple
from contextlib import contextmanager
from traceback import format_exception

__all__ = [
    "Health",
    "expect_exception"
]

_Error = namedtuple("_Error", "source reason exception")


@contextmanager
def expect_exception(health):
    try:
        yield health
    except Exception as exc:
        health.add_exception(exc)


class Health(object):

    def __init__(self):
        self._errors = []

    @property
    def ok(self):
        return not self._errors

    @property
    def details(self):
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

    def add_exception(self, exc):
        tb = "".join(format_exception(type(exc), exc, exc.__traceback__))
        self._errors.append(_Error(None, "exception", tb))
        return self
