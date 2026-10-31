# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_indent import token_indent

lTokens = []
lTokens.append(token.attribute_specification.attribute_keyword)


class rule_300(token_indent):
    """
    This rule checks the indent of the **attribute** keyword.

    **Violation**

    .. code-block:: vhdl

       signal sig1 : std_logic;
          attribute coordinate of comp_1 : component is (0.0, 17.5);

    **Fix**

    .. code-block:: vhdl

       signal sig1 : std_logic;
       attribute coordinate of comp_1 : component is (0.0, 17.5);
    """

    def __init__(self):
        super().__init__(lTokens)
