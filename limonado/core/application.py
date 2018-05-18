# -*- coding: utf-8 -*-

import tornado.web


class Application(tornado.web.Application):
    def __init__(self, settings, **kwargs):
        super(Application, self).__init__(**kwargs)
        self.name = settings["name"]
        self.id = settings["id"]
        self.version = settings["version"]
        self.server = settings["server"]
