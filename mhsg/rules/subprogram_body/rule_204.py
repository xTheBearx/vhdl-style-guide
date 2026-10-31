# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.blank_line_above_line_starting_with_token import (
    blank_line_above_line_starting_with_token,
)

lTokens = []
lTokens.append(token.subprogram_body.end_keyword)


class rule_204(blank_line_above_line_starting_with_token):
    """
    This rule checks for blank lines above the **end** keyword.

    |configuring_blank_lines_link|

    **Violation**

    .. code-block:: vhdl

       begin

         a <= b;
       end function overflow;

    **Fix**

    .. code-block:: vhdl

       begin

         a <= b;

       end function overflow;
    """

    def __init__(self):
        super().__init__(lTokens)
