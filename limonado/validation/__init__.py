# -*- coding: utf-8 -*-

from functools import wraps

import jsonschema
from tornado.concurrent import is_future
from tornado.gen import coroutine

from ..exceptions import APIError
from ..log import log
from ..utils.decorators import container
from ..utils.validators import validate_duration

__all__ = ["format_checker"]

format_checker = jsonschema.FormatChecker()


def register_format(name, validator):
    format_checker.checks(name)(validator)


register_format("duration", validate_duration)


def validate_response(schema):
    @container
    def _validate(rh_method):
        @wraps(rh_method)
        @coroutine
        def _wrapper(self, *args, **kwargs):
            result = rh_method(self, *args, **kwargs)
            if is_future(result):
                result = yield result

            if result is not None:
                try:
                    jsonschema.validate(
                        result, schema, format_checker=self.format_checker)
                except jsonschema.ValidationError:
                    log.exception("Invalid response")
                    raise APIError(500)

                self.write_json(result)
                self.finish()

        return _wrapper

    return _validate
