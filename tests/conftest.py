# -*- coding: utf-8 -*-
"""
The rule tests were written for 2-space indentation and lines of 120 characters, the defaults before they became
4 and 80. Tests that create rules in this process keep those settings, so their files stay as they were reviewed;
tests/mhsg/test_defaults.py checks the defaults themselves, and tests that run mhsg as a program use the defaults.
"""

import importlib

import pytest

from mhsg import rule

# mhsg.rules exports the class line_length under the name of its module
line_length = importlib.import_module("mhsg.rules.line_length")

TEST_INDENT_SIZE = 2
TEST_LINE_LENGTH = 120


@pytest.fixture(autouse=True)
def rule_test_defaults(request, monkeypatch):
    if request.node.get_closest_marker("current_defaults"):
        return
    monkeypatch.setattr(rule, "DEFAULT_INDENT_SIZE", TEST_INDENT_SIZE)
    monkeypatch.setattr(line_length, "DEFAULT_LENGTH", TEST_LINE_LENGTH)


def pytest_configure(config):
    config.addinivalue_line("markers", "current_defaults: run with the current default indent size and line length")
