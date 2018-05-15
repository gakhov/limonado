# -*- coding: utf-8 -*-

from tornado.escape import json_decode
from tornado.escape import json_encode
from tornado.gen import coroutine
from tornado.web import RequestHandler

from .exceptions import APIError
from .utils._params import extract_params
from .validation import schemas
from .validation import validate_request_data
from .validation import validate_response

__all__ = [
    "EndpointHandler",
    "HealthHandler"
]


class EndpointHandler(RequestHandler):
    """Base class for endpoint"s handlers."""

    def __init__(self, *args, **kwargs):
        super(EndpointHandler, self).__init__(*args, **kwargs)
        self.params = {}
        self.json = None

    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")
        self.set_header("Api", self.application.name)
        self.set_header("Api-Version", self.application.version)
        self.set_header("Server", self.application.server)

    def initialize(self, endpoint):
        self.endpoint = endpoint

    def write_error(self, status_code, **kwargs):
        self.clear()
        self.set_status(status_code)
        error = {
            "code": status_code,
            "message": self._reason
        }
        exception = kwargs["exc_info"][1]
        if isinstance(exception, APIError):
            error["error"] = {
                "message": exception.message
            }
            if exception.details:
                error["error"].update(exception.details)

        self.write_json(error)

    def get_params(self, schema):
        params = extract_params(self.request.arguments, schema)
        validate_request_data(params, schema)
        return params

    def get_json(self, schema=None):
        if not self.request.body:
            return None

        try:
            json = json_decode(self.request.body.decode("utf-8"))
        except ValueError:
            raise APIError(400, "Malformed JSON")
        else:
            if schema is not None:
                validate_request_data(json, schema)

            return json

    def write_json(self, value):
        self.write(json_encode(value))


class HealthHandler(EndpointHandler):

    response_schema = schemas.HEALTH

    @coroutine
    def head(self):
        health = yield self.check_health()
        if not health.ok:
            self.set_status(503)
        else:
            self.set_status(200)

        self.finish()

    @validate_response(response_schema)
    @coroutine
    def get(self):
        health = yield self.check_health()
        if not health.ok:
            self.set_status(503)

        return health.details

    def check_health(self):
        return self.endpoint.check_health()
