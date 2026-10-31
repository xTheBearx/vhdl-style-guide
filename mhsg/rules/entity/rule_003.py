# -*- coding: utf-8 -*-

from mhsg.rules.previous_line import previous_line
from mhsg.token import entity_declaration as token


class rule_003(previous_line):
    """
    This rule checks for blank lines or comments above the **entity** keyword.

    |configuring_previous_line_rules_link|

    **Violation**

    .. code-block:: vhdl

       library ieee;
       entity fifo is

    **Fix**

    .. code-block:: vhdl

       library ieee;

       entity fifo is
    """

    def __init__(self):
        super().__init__([token.entity_keyword])
