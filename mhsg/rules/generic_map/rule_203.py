# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules import previous_line as Rule

lTokens = []
lTokens.append(token.generic_map_aspect.generic_keyword)


class rule_203(Rule):
    """
    This rule checks for blank lines or comments above the **generic map** keywords.

    |configuring_previous_line_rules_link|

    The default style is :code:`no_blank_line`.

    **Violation**

    .. code-block:: vhdl

      U_FIFO : FIFO

        generic map (
          G_WIDTH => 8
        )

    **Fix**

    .. code-block:: vhdl

      U_FIFO : FIFO
        generic map (
          G_WIDTH => 8
        )
    """

    def __init__(self):
        super().__init__(lTokens)
        self.style = "no_blank_line"
