# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from argparse import Action
from argparse import ArgumentError
from argparse import ArgumentParser
from argparse import ArgumentTypeError
import collections
import errno
import json
import logging
import sys

__all__ = ["BaseCli", "run"]

log = logging.getLogger(__name__)


class BaseCli:
    def __init__(self, loader=json.load):
        self.loader = loader

    def add_arguments(self, parser):
        pass

    def create_api(self, args):
        raise NotImplementedError

    def run(self):
        parser = self.create_parser()
        args = parser.parse_args()
        api = self.create_api(args)
        settings = args.settings
        _add_inline_settings(args.inline_settings, settings)
        api.settings.update(settings)
        if args.disable:
            enable = api.endpoint_names - set(args.disable)
        else:
            enable = args.enable or None

        log.info("Starting server '%s' on %s:%i", api.settings["id"],
                 args.address, args.port)
        try:
            api.run(port=args.port, address=args.address, enable=enable)
        except:
            log.exception("Failed to start server '%s' on %s:%i",
                          api.settings["id"], args.address, args.port)
            sys.exit(errno.EINTR)

    def create_parser(self):
        parser = ArgumentParser()
        parser.add_argument("--port", type=int, default=8000)
        parser.add_argument("--address", default="")
        parser.add_argument("--enable", action="append")
        parser.add_argument("--disable", action="append")
        parser.add_argument(
            "--settings", type=_SettingsType(self.loader), default={})
        parser.add_argument(
            "--set",
            dest="inline_settings",
            action=_AppendSettingAction,
            default=[])
        self.add_arguments(parser)
        return parser


def run(api, **kwargs):
    class Cli(BaseCli):
        def create_api(self, args):
            return api

    Cli(**kwargs).run()


def _add_inline_settings(inline_settings, settings):
    for path, value in inline_settings:
        keys = path.split(".")
        current = settings
        for key in keys[:-1]:
            current = current.setdefault(key, {})

        current[keys[-1]] = value


def _parse_inline_value(string):
    string = string.strip()
    if _is_unqouted_string(string):
        string = '"{}"'.format(string)

    return json.loads(string)


def _is_unqouted_string(string):
    if (string.startswith(('"', "{", "["))
            or string in ("null", "true", "false")):
        return False

    for factory in (float, int):
        try:
            factory(string)
        except ValueError:
            pass
        else:
            return False

    return True


class _AppendSettingAction(Action):
    def __init__(self,
                 option_strings,
                 dest,
                 default=None,
                 required=False,
                 help=None,
                 metavar=None):
        super(_AppendSettingAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=2,
            default=default,
            required=required,
            help=help,
            metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        name, raw_value = values
        try:
            value = _parse_inline_value(raw_value)
        except ValueError as error:
            raise ArgumentError(self, "bad value: {}".format(error))

        items = getattr(namespace, self.dest, None)
        if items is None:
            items = []

        items.append((name, value))
        setattr(namespace, self.dest, items)


class _SettingsType:
    def __init__(self, loader):
        self.loader = loader

    def __call__(self, path):
        try:
            handle = open(path)
        except OSError:
            raise ArgumentTypeError("can't open '{}'".format(path))
        else:
            settings = self._load(handle)
            handle.close()
            return settings

    def _load(self, handle):
        try:
            settings = self.loader(handle)
        except Exception as exc:
            raise ArgumentTypeError("can't load settings: {}".format(exc))
        else:
            if not isinstance(settings, collections.Mapping):
                raise ArgumentTypeError("settings must be a mapping")

            return settings

    def __repr__(self):
        return "{}()".format(self.__class__.__name__)
