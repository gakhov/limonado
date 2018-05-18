# -*- coding: utf-8 -*-

from functools import wraps
import logging

import jsonschema
from tornado.concurrent import is_future
from tornado.gen import coroutine

from ..exceptions import APIError
from ..utils.decorators import container
from ..utils.validators import validate_duration

__all__ = ["format_checker", "validate_response"]

log = logging.getLogger(__name__)

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
                        result, schema, format_checker=format_checker)
                except jsonschema.ValidationError:
                    log.exception("Invalid response")
                    raise APIError(500, "Invalid response")

                self.write_json(result)
                self.finish()

        return _wrapper

    return _validate


def validate_request_data(data, schema):
    try:
        jsonschema.validate(data, schema, format_checker=format_checker)
    except jsonschema.ValidationError as error:
        raise APIError(400, error.message, details=_get_details(error))


def _get_details(error):
    path = ["root"]
    for item in error.absolute_path:
        if isinstance(item, int):
            fmt = "[{}]"
        else:
            fmt = ".{}"

        path.append(fmt.format(item))

    return {"path": "".join(path)}
