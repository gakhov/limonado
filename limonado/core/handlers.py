# -*- coding: utf-8 -*-

import jsonschema

from tornado.escape import json_decode
from tornado.escape import json_encode
import tornado.web

from ..__about__ import __version__
from ..exceptions import APIError
from ..utils import generate_uuid
from ..utils._params import extract_params
from ..validation import format_checker

__all__ = ["ErrorHandler", "RequestHandler"]


class RequestHandler(tornado.web.RequestHandler):
    @property
    def request_id(self):
        if not hasattr(self, "_request_id"):
            self._request_id = generate_uuid()

        return self._request_id

    @property
    def format_checker(self):
        return format_checker

    def json_encode(self, value):
        return json_encode(value)

    def json_decode(self, value):
        return json_decode(value)

    def set_default_headers(self):
        self.set_header("Request-Id", self.request_id)
        self.set_header("Content-Type", "application/json")
        self.set_header("Api", self.application.api.name)
        self.set_header("Api-Version", self.application.api.version)
        self.set_header("Server", "Limonado/{}".format(__version__))

    def get_params(self, schema):
        params = extract_params(self.request.arguments, schema)
        self._validate_request_data(params, schema)
        return params

    def get_json(self, schema=None):
        if not self.request.body:
            return None

        try:
            json = self.json_decode(self.request.body.decode("utf-8"))
        except ValueError:
            raise APIError(400, "Malformed JSON")
        else:
            if schema is not None:
                self._validate_request_data(json, schema)

            return json

    def write_json(self, value):
        self.write(self.json_encode(value))

    def write_error(self, status_code, **kwargs):
        self.clear()
        self.set_status(status_code)
        error = {"code": status_code, "message": self._reason}
        exception = kwargs["exc_info"][1]
        if isinstance(exception, APIError):
            error["error"] = {"message": exception.message}
            if exception.details:
                error["error"].update(exception.details)

        self.write_json(error)

    def _request_summary(self):
        return "{method} {uri} {id} ({remote_ip})".format(
            method=self.request.method,
            uri=self.request.uri,
            id=self.request_id,
            remote_ip=self.request.remote_ip)

    def _validate_request_data(self, data, schema):
        try:
            jsonschema.validate(
                data, schema, format_checker=self.format_checker)
        except jsonschema.ValidationError as error:
            raise APIError(
                400, error.message, details=_get_error_details(error))


class ErrorHandler(tornado.web.ErrorHandler, RequestHandler):
    pass


def _get_error_details(error):
    path = ["root"]
    for item in error.absolute_path:
        if isinstance(item, int):
            fmt = "[{}]"
        else:
            fmt = ".{}"

        path.append(fmt.format(item))

    return {"path": "".join(path)}
