# -*- encoding: utf-8 -*-

from tornado.web import HTTPError

__all__ = [
    "APIError"
]


class APIError(HTTPError):

    def __init__(self, status_code, message=None, details=None, **kwargs):
        super(APIError, self).__init__(status_code, **kwargs)
        self.message = message
        self.details = details
