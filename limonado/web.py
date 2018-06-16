# -*- coding: utf-8 -*-

import os
import signal
import time

from tornado.gen import coroutine
from tornado.ioloop import IOLoop

from . import utils
from .core.application import Application
from .core.api import API
from .core.handlers import ErrorHandler
from .log import log

__all__ = ["WebAPI", "run"]

_ENV = os.environ.get("LIMONADO_ENV") or "production"
_DEBUG = _ENV == "development"


def run(api_or_coro,
        *,
        port=8000,
        address="",
        handle_signals=False,
        signals=(signal.SIGTERM, ),
        shutdown_timeout=3.0,
        **kwargs):
    loop = IOLoop.current()
    if callable(api_or_coro):
        api = loop.run_sync(lambda: api_or_coro(loop))
    else:
        api = api_or_coro

    app = api.get_application(**kwargs)
    server = app.listen(port, address=address)
    if handle_signals:
        _handle_signals(signals, loop, server, shutdown_timeout)

    loop.start()


class WebAPI(API):
    def __init__(self, name, *, version="1", prefix="", debug=_DEBUG):
        super().__init__()
        self.name = name
        self.version = version
        self.prefix = prefix
        self.debug = debug

    @property
    def base_path(self):
        return utils.join_paths(self.prefix, "/v{}".format(self.version))

    def get_application(self):
        handlers = list(self.iter_handlers(base_path=self.base_path))
        for handler in handlers:
            log.info("Endpoint: %s", handler[0])

        init_start_time = time.time()
        IOLoop.current().run_sync(self._initialize_apis)
        log.info("Initialized in %.1f seconds", time.time() - init_start_time)
        return Application(
            self,
            handlers=handlers,
            default_handler_class=ErrorHandler,
            default_handler_args={"status_code": 404})

    @coroutine
    def _initialize_apis(self):
        # Traverse the tree of APIs and collect all initializers.
        initializers = [self.initialize]
        initializers.extend(
            api.initialize for api in self.iter_subapis(max_depth=None))
        # Run initializers in parallel.
        yield [initializer() for initializer in initializers]


def _handle_signals(signals, loop, server, shutdown_timeout):
    def handle_signal(signum, frame):
        log.warning("Signal received: %s", signal.Signals(signum).name)
        loop.add_callback(shutdown)

    def shutdown():
        # Stop accepting new connections.
        server.stop()
        log.warning("Shutting down in %.1f seconds ...", shutdown_timeout)
        # Give pending tasks some time to finish.
        loop.add_timeout(time.time() + shutdown_timeout, loop.stop)

    for signum in signals:
        signal.signal(signum, handle_signal)
