# -*- coding: utf-8 -*-

import uuid

from tornado.escape import json_decode
from tornado.escape import json_encode
import tornado.web

from ..exceptions import APIError
from ..utils._params import extract_params
from ..validation import validate_request_data

__all__ = ["ErrorHandler", "RequestHandler"]


class RequestHandler(tornado.web.RequestHandler):
    @property
    def request_id(self):
        if not hasattr(self, "_request_id"):
            self._request_id = uuid.uuid4().hex

        return self._request_id

    def set_default_headers(self):
        self.set_header("Request-Id", self.request_id)
        self.set_header("Content-Type", "application/json")
        self.set_header("Api", self.application.name)
        self.set_header("Api-Version", self.application.version)
        self.set_header("Server", self.application.server)

    def json_encode(self, value):
        return json_encode(value)

    def json_decode(self, value):
        return json_decode(value)

    def get_params(self, schema):
        params = extract_params(self.request.arguments, schema)
        validate_request_data(params, schema)
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
                validate_request_data(json, schema)

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
            id=self.request_id,
            method=self.request.method,
            uri=self.request.uri,
            remote_ip=self.request.remote_ip)


class ErrorHandler(tornado.web.ErrorHandler, RequestHandler):
    pass
