# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules import token_indent

lTokens = []
lTokens.append(token.attribute_declaration.attribute_keyword)


class rule_300(token_indent):
    """
    This rule checks the indent of the **attribute** keyword.

    **Violation**

    .. code-block:: vhdl

       signal sig1 : std_logic;
          attribute max_delay : time;

    **Fix**

    .. code-block:: vhdl

       signal sig1 : std_logic;
       attribute max_delay : time;
    """

    def __init__(self):
        super().__init__(lTokens)
