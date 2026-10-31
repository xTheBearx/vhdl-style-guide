# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.blank_line_below_line_ending_with_token import (
    blank_line_below_line_ending_with_token as Rule,
)

lTokens = []
lTokens.append(token.generic_map_aspect.open_parenthesis)


class rule_200(Rule):
    """
    This rule checks for a blank line below the open parenthesis in a generic map.

    |configuring_blank_lines_link|

    The default style is :code:`no_blank_line`.

    **Violation**

    .. code-block:: vhdl

      generic map (

        G_WIDTH => 8,
        G_DEPTH => 16
      )

    **Fix**

    .. code-block:: vhdl

      generic map (
        G_WIDTH => 8,
        G_DEPTH => 16
      )
    """

    def __init__(self):
        super().__init__(lTokens)
        self.style = "no_blank_line"
