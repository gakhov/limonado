# -*- coding: utf-8 -*-

from functools import wraps
import logging

import jsonschema
from tornado.concurrent import is_future
from tornado.escape import json_decode
from tornado.gen import coroutine

from ._params import extract_params
from ._validators import validate_duration
from .exceptions import APIError
from .utils import container

__all__ = [
    "format_checker",
    "validate_request",
    "validate_response"
]

log = logging.getLogger(__name__)

format_checker = jsonschema.FormatChecker()
format_checker.checks("duration")(validate_duration)


def validate_request(params_schema=None, json_schema=None):

    @container
    def _validate(rh_method):

        @wraps(rh_method)
        def _wrapper(self, *args, **kwargs):
            if params_schema is None:
                params = {}
            else:
                params = extract_params(self.request.arguments, params_schema)
                _validate_request_data(params, params_schema)

            if not self.request.body:
                json = None
            else:
                try:
                    json = json_decode(self.request.body.decode("utf-8"))
                except ValueError:
                    raise APIError(400, "Malformed JSON")

            if json_schema is not None:
                _validate_request_data(json, json_schema)

            self.params = params
            self.json = json
            return rh_method(self, *args, **kwargs)

        return _wrapper

    return _validate


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
                    jsonschema.validate(result, schema,
                                        format_checker=format_checker)
                except jsonschema.ValidationError:
                    log.exception("Invalid response")
                    raise APIError(500, "Invalid response")

                self.write_json(result)
                self.finish()

        return _wrapper

    return _validate


def _validate_request_data(data, schema):
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

    return {
        "path": "".join(path),
    }
