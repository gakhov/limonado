# -*- coding: utf-8 -*-

import tornado.web


class Application(tornado.web.Application):
    def __init__(self, config, **kwargs):
        kwargs.setdefault("debug", config["debug"])
        super().__init__(**kwargs)
        self.config = config
