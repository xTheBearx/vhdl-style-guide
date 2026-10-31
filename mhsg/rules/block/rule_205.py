# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.blank_line_below_line_ending_with_token import (
    blank_line_below_line_ending_with_token,
)

lTokens = []
lTokens.append(token.block_statement.semicolon)


class rule_205(blank_line_below_line_ending_with_token):
    """
    This rule checks for a blank line below the semicolon.

    |configuring_blank_lines_link|

    **Violation**

    .. code-block:: vhdl

       end block block_label;
       a <= b;

    **Fix**

    .. code-block:: vhdl

       end block block_label;

       a <= b;
    """

    def __init__(self):
        super().__init__(lTokens)
