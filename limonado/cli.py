# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import argparse
import errno
import logging
import sys

import tornado.ioloop

from ._cli import AppendSettingAction
from ._cli import SettingsType
from ._cli import add_inline_settings

__all__ = [
    "run_cli",
]

log = logging.getLogger(__name__)

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--name")
arg_parser.add_argument("--port", type=int)
arg_parser.add_argument("--enable", action="append")
arg_parser.add_argument("--disable", action="append")
arg_parser.add_argument("--settings", type=SettingsType(), default={})
arg_parser.add_argument("--set", dest="inline_settings",
                        action=AppendSettingAction, default=[])


def run_cli(api):
    args = arg_parser.parse_args()
    settings = args.settings
    add_inline_settings(args.inline_settings, settings)
    name = args.name or api.settings["name"]
    port = args.port or api.settings["port"]
    api.settings["name"] = name
    api.settings["port"] = port
    api.settings.update(settings)
    if args.disable:
        enable = api.endpoint_names - set(args.disable)
    else:
        enable = args.enable or None

    log.info("Starting server '%s' on port %i", name, port)
    try:
        app = api.get_application(enable=enable)
        app.listen(port)
        tornado.ioloop.IOLoop.instance().start()
    except:
        raise
        log.exception("Failed to start server '%s' on port %i", name, port)
        sys.exit(errno.EINTR)
