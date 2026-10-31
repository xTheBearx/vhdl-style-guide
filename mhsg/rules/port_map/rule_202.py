# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules import previous_line as Rule

lTokens = []
lTokens.append(token.port_map_aspect.close_parenthesis)


class rule_202(Rule):
    """
    This rule checks for blank lines or comments above the closing parenthesis in a port map.

    |configuring_previous_line_rules_link|

    The default style is :code:`no_blank_line`.

    **Violation**

    .. code-block:: vhdl

      port map (
        WR_EN => w_wr_en,
        RD_EN => w_rd_en

      );

    **Fix**

    .. code-block:: vhdl

      port map (
        WR_EN => w_wr_en,
        RD_EN => w_rd_en
      );
    """

    def __init__(self):
        super().__init__(lTokens)
        self.style = "no_blank_line"
