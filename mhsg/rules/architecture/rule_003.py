# -*- coding: utf-8 -*-

from mhsg.rules.previous_line import previous_line
from mhsg.token import architecture_body as token


class rule_003(previous_line):
    """
    This rule checks for a blank lines or comments above the **architecture** declaration.

    |configuring_previous_line_rules_link|

    **Violation**

    .. code-block:: vhdl

       library ieee;
       architecture rtl of fifo is

    **Fix**

    .. code-block:: vhdl

       library ieee;

       architecture rtl of fifo is
    """

    def __init__(self):
        super().__init__([token.architecture_keyword])
        self.style = "require_blank_line"
