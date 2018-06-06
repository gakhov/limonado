# -*- coding: utf-8 -*-

from argparse import Action
from argparse import ArgumentError
from argparse import ArgumentParser
from argparse import ArgumentTypeError
import collections
import errno
import json
import sys

from .log import log

__all__ = ["BaseCli", "run"]


class BaseCli:
    def __init__(self, config_loader=json.load):
        self.config_loader = config_loader

    def add_arguments(self, parser):
        pass

    def create_api(self, args):
        raise NotImplementedError

    def run(self):
        parser = self.create_parser()
        args = parser.parse_args()
        api = self.create_api(args)
        _add_inline_settings(args.inline_settings, args.config)
        api.config.update(args.config)
        if args.disable:
            enable = api.endpoint_names - set(args.disable)
        else:
            enable = args.enable or None

        log.info("Starting server '%s' on %s:%i", api.config["id"],
                 args.address, args.port)
        try:
            api.run(port=args.port, address=args.address, enable=enable)
        except Exception as exc:
            log.critical(
                "Failed to start server '%s' on %s:%i",
                api.config["id"],
                args.address,
                args.port,
                exc_info=exc)
            sys.exit(errno.EINTR)

    def create_parser(self):
        parser = ArgumentParser()
        parser.add_argument("--port", type=int, default=8000)
        parser.add_argument("--address", default="")
        parser.add_argument("--enable", action="append")
        parser.add_argument("--disable", action="append")
        parser.add_argument(
            "--config", type=_ConfigType(self.config_loader), default={})
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


def _add_inline_settings(inline_settings, config):
    for path, value in inline_settings:
        keys = path.split(".")
        current = config
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
        super().__init__(
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


class _ConfigType:
    def __init__(self, loader):
        self.loader = loader

    def __call__(self, path):
        try:
            handle = open(path)
        except OSError:
            raise ArgumentTypeError("can't open '{}'".format(path))
        else:
            config = self._load(handle)
            handle.close()
            return config

    def _load(self, handle):
        try:
            config = self.loader(handle)
        except Exception as exc:
            raise ArgumentTypeError("can't load config: {}".format(exc))
        else:
            if not isinstance(config, collections.Mapping):
                raise ArgumentTypeError("config must be a mapping")

            return config

    def __repr__(self):
        return "{}()".format(self.__class__.__name__)
