# -*- coding: utf-8 -*-


class Context:
    def __init__(self, settings, executor, **kwargs):
        self._settings = settings
        self._executor = executor
        for name, value in kwargs.items():
            assert not name.startswith("_"), "internal name"
            assert name not in ("settings", "executor"), "reserved name"
            setattr(self, name, value)

    @property
    def settings(self):
        return self._settings

    @property
    def executor(self):
        return self._executor
