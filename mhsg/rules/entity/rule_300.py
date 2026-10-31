# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_indent import token_indent as Rule

lTokens = []
lTokens.append(token.entity_declaration.begin_keyword)


class rule_300(Rule):
    """
    This rule checks the indent of the **begin** keyword.

    **Violation**

    .. code-block:: vhdl

       entity FIFO is

            begin

    **Fix**

    .. code-block:: vhdl

       entity FIFO is

       begin
    """

    def __init__(self):
        super().__init__(lTokens)
