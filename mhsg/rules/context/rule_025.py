# -*- coding: utf-8 -*-

from mhsg.rules import blank_line_below_line_ending_with_token
from mhsg.token import context_declaration as token


class rule_025(blank_line_below_line_ending_with_token):
    """
    This rule adds a blank line below the context semicolon.

    |configuring_blank_lines_link|

    **Violation**

    .. code-block:: vhdl

       end context;
       entity fifo is

    **Fix**

    .. code-block:: vhdl

       end context;

       entity fifo is
    """

    def __init__(self):
        super().__init__([token.semicolon])
