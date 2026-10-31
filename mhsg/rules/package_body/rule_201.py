# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.blank_line_below_line_ending_with_token import (
    blank_line_below_line_ending_with_token,
)

lTokens = []
lTokens.append(token.package_body.is_keyword)


class rule_201(blank_line_below_line_ending_with_token):
    """
    This rule checks for a blank line below the **package** keyword.

    |configuring_blank_lines_link|

    **Violation**

    .. code-block:: vhdl

       package body FIFO_PKG is
         constant width : integer := 32;

    **Fix**

    .. code-block:: vhdl

       package body FIFO_PKG is

         constant width : integer := 32;
    """

    def __init__(self):
        super().__init__(lTokens)
