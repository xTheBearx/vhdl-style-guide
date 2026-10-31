# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.previous_line import previous_line as Rule

lTokens = []
lTokens.append(token.generic_map_aspect.close_parenthesis)


class rule_202(Rule):
    """
    This rule checks for blank lines or comments above the closing parenthesis in a generic map.

    |configuring_previous_line_rules_link|

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
