# -*- coding: utf-8 -*-

import argparse
import collections
import json


__all__ = [
    "SettingsType",
    "AppendSettingAction",
    "add_inline_settings"
]


def load_settings(path_or_str):

    def load():
        """Load JSON from a string or path (starts with @)."""
        if not path_or_str.startswith("@"):
            return json.loads(path_or_str)

        with open(path_or_str[1:], "r") as handle:
            return json.load(handle)

    settings = load()
    if not isinstance(settings, collections.Mapping):
        raise TypeError("settings must be a mapping")

    return settings


def add_inline_settings(inline_settings, settings):
    for path, value in inline_settings:
        set_inline(path, value, settings)


def set_inline(path, value, settings):
    keys = path.split(".")
    current = settings
    for key in keys[:-1]:
        current = current.setdefault(key, {})

    current[keys[-1]] = value


class SettingsType(object):

    def __call__(self, string):
        return load_settings(string)

    def __repr__(self):
        return "{}()".format(self.__class__.__name__)


class AppendSettingAction(argparse.Action):

    def __init__(self,
                 option_strings,
                 dest,
                 default=None,
                 required=False,
                 help=None,
                 metavar=None):
        super(AppendSettingAction, self).__init__(
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
            value = json.loads(raw_value)
        except ValueError:
            raise argparse.ArgumentError(self, "value must be valid JSON")

        items = getattr(namespace, self.dest, None)
        if items is None:
            items = []

        items.append((name, value))
        setattr(namespace, self.dest, items)
