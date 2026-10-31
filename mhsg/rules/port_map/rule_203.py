# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.previous_line import previous_line as Rule

lTokens = []
lTokens.append(token.port_map_aspect.port_keyword)


class rule_203(Rule):
    """
    This rule checks for blank lines or comments above the **port map** keywords.

    |configuring_previous_line_rules_link|

    The default style is :code:`no_blank_line`.

    **Violation**

    .. code-block:: vhdl

      U_FIFO : FIFO
        generic map (
          G_WIDTH => 8
        )

        port map (
          WR_EN => w_wr_en
        );

    **Fix**

    .. code-block:: vhdl

      U_FIFO : FIFO
        generic map (
          G_WIDTH => 8
        )
        port map (
          WR_EN => w_wr_en
        );
    """

    def __init__(self):
        super().__init__(lTokens)
        self.style = "no_blank_line"
