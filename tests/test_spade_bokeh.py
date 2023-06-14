#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `spade_bokeh` package."""
from collections import namedtuple

import pytest

from spade_bokeh import spade_bokeh


@pytest.fixture
def agent():
    return namedtuple("agent", "port")(port=1024)


def test_server(agent):
    server = spade_bokeh.BokekServer(agent)

    assert server.agent.port == 1024
    assert not server.hostname
    assert not server.port
    assert not server.server
    assert not server.is_running


def test_add_plot(agent):
    server = spade_bokeh.BokekServer(agent)

    server.add_plot("/my_plot", lambda x: x)

    assert "/my_plot" in server.apps


def test_get_plot_script():
    server = spade_bokeh.BokekServer(agent)
    server.hostname = "hostname"
    server.port = 1024

    server.add_plot("/my_plot", lambda x: x)

    script = server.get_plot_script("/my_plot")

    assert type(script) == str
    assert script.startswith("<script ")
    assert "bokeh-absolute-url=http://hostname:1024/my_plot" in script
    assert script.endswith("</script>")
