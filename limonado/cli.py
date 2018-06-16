# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from argparse import ArgumentTypeError
import errno
import json
import sys

from .web import run as run_api
from .log import log

__all__ = ["BaseCLI", "run"]


class BaseCLI:
    def __init__(self, config_loader=json.load):
        self.config_loader = config_loader

    def add_arguments(self, parser):
        pass

    def create_api(self, args):
        raise NotImplementedError

    def run(self, **kwargs):
        parser = self.create_parser()
        args = parser.parse_args()
        api = self.create_api(args)
        log.info("Starting server on %s:%i", args.address, args.port)
        try:
            run_api(api, port=args.port, address=args.address, **kwargs)
        except Exception as exc:
            log.critical(
                "Failed to start server on %s:%i",
                args.address,
                args.port,
                exc_info=exc)
            sys.exit(errno.EINTR)

    def create_parser(self):
        parser = ArgumentParser()
        parser.add_argument("--port", type=int, default=8000)
        parser.add_argument("--address", default="")
        parser.add_argument(
            "--config",
            metavar="PATH",
            type=_ConfigType(self.config_loader),
            default={})
        self.add_arguments(parser)
        return parser


def run(api, cli_kwargs=None, **kwargs):
    class CLI(BaseCLI):
        def create_api(self, args):
            return api

    CLI(**(cli_kwargs or {})).run(**kwargs)


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
            return config

    def __repr__(self):
        return "{}()".format(self.__class__.__name__)
