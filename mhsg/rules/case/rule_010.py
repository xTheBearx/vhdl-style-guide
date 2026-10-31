# -*- coding: utf-8 -*-

from mhsg.rules import blank_line_below_line_ending_with_token
from mhsg.token import case_statement as token


class rule_010(blank_line_below_line_ending_with_token):
    """
    This rule checks for a blank line below the **end case** keywords.

    |configuring_blank_lines_link|

    **Violation**

    .. code-block:: vhdl

       end case;
       a <= '1';

    **Fix**

    .. code-block:: vhdl

       end case;

       a <= '1';
    """

    def __init__(self):
        super().__init__([token.semicolon])
