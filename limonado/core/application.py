# -*- coding: utf-8 -*-

import tornado.web


class Application(tornado.web.Application):
    def __init__(self, api, **kwargs):
        kwargs.setdefault("debug", api.debug)
        super().__init__(**kwargs)
        self.api = api
