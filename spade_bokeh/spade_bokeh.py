# -*- coding: utf-8 -*-

import asyncio
from threading import Thread

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.server.server import BaseServer
from bokeh.server.tornado import BokehTornado
from bokeh.server.util import bind_sockets
from bokeh.embed import server_document


class BokekServer(object):

    def __init__(self, agent):
        self.hostname = None
        self.port = None
        self.agent = agent
        self.thread = Thread(target=self.bokeh_worker)
        self.server = None
        self.is_running = False

        self.apps = {}

    def start(self, hostname="localhost", port=5006):
        """
        Starts the bokeh server.
        Args:
            hostname (str): hostname of the server. Must be the same where the agent is running. Defaults to "localhost"
            port (int): port of the server. Defaults to 5006.

        """
        self.hostname = hostname
        self.port = port
        self.thread.start()
        self.is_running = True

    def stop(self):
        """
        Stops the Bokeh server.

        """
        if self.server:
            self.server.stop()
            self.is_running = False

    def bokeh_worker(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        sockets, port = bind_sockets(self.hostname, self.port)

        extra_websocket_origins = ["{}:{}".format(self.hostname, self.port),
                                   "{}:{}".format(self.hostname, self.agent.web.port)]
        bokeh_tornado = BokehTornado(self.apps, extra_websocket_origins=extra_websocket_origins)
        bokeh_http = HTTPServer(bokeh_tornado)
        bokeh_http.add_sockets(sockets)

        self.server = BaseServer(IOLoop.current(), bokeh_tornado, bokeh_http)
        self.server.start()
        self.server.io_loop.start()

    def get_plot_script(self, path):
        """
        Returns the necessary javascript to render a plot
        Args:
            path (str): the path with which the plot was registered in the server.

        Returns:
            A string with the javascript code to render the plot.

        """
        return server_document("http://{hostname}:{port}{path}".format(hostname=self.hostname,
                                                                       port=self.port,
                                                                       path=path))

    def add_plot(self, path, func):
        """
        Registers a new plot in the bokeh server.
        Args:
            path: path where the plot will respond to queries
            func: the function that renders the plot.

        """
        self.apps[path] = Application(FunctionHandler(func))


class BokehServerMixin(object):
    """
    This is the Mixin to inherit from when you create your agent.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bokeh_server = BokekServer(agent=self)
