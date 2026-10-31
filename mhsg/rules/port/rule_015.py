# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_indent import token_indent

lTokens = []
lTokens.append(token.port_clause.close_parenthesis)


class rule_015(token_indent):
    """
    This rule checks the indent of the closing parenthesis for port clauses.

    **Violation**

    .. code-block:: vhdl

       port (
         WR_EN    : in    std_logic;
         RD_EN    : in    std_logic;
         OVERFLOW : out   std_logic;
         DATA     : inout std_logic
         );

    **Fix**

    .. code-block:: vhdl

       port (
         WR_EN    : in    std_logic;
         RD_EN    : in    std_logic;
         OVERFLOW : out   std_logic;
         DATA     : inout std_logic
       );
    """

    def __init__(self):
        super().__init__(lTokens)
