# -*- coding: utf-8 -*-


class Context:
    def __init__(self, config, executor, **kwargs):
        self._config = config
        self._executor = executor
        for name, value in kwargs.items():
            assert not name.startswith("_"), "internal name"
            assert name not in ("config", "executor"), "reserved name"
            setattr(self, name, value)

    @property
    def config(self):
        return self._config

    @property
    def executor(self):
        return self._executor
