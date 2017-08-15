# -*- coding: utf-8 -*-

from copy import deepcopy

DEFAULT_EXECUTOR = "default"


class Context(object):

    def __init__(self, settings, executors, **kwargs):
        self._settings = deepcopy(settings)
        if DEFAULT_EXECUTOR not in executors:
            raise ValueError("missing '{}' executor".format(DEFAULT_EXECUTOR))

        self._executors = dict(executors)
        for name, value in kwargs.items():
            setattr(self, name, value)

    @property
    def settings(self):
        return self._settings

    @property
    def executors(self):
        return self._executors

    @property
    def default_executor(self):
        return self._executors[DEFAULT_EXECUTOR]
