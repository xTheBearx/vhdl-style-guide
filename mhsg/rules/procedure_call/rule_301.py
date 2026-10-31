# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules import token_indent

lTokens = []
lTokens.append(token.concurrent_procedure_call_statement.postponed_keyword)


class rule_301(token_indent):
    """
    This rule checks the indent of the **postponed** keyword if it exists..

    **Violation**

    .. code-block:: vhdl

       a <= b;

         postponed WR_EN(parameter);

    **Fix**

    .. code-block:: vhdl

       a <= b;

       postponed WR_EN(parameter);
    """

    def __init__(self):
        super().__init__(lTokens)
