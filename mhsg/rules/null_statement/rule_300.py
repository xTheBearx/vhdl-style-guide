# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_indent import token_indent as Rule

lTokens = []
lTokens.append(token.null_statement.null_keyword)


class rule_300(Rule):
    """
    This rule checks the indentation of the **null** keyword.

    **Violation**

    .. code-block:: vhdl

         null;
         end loop;

    **Fix**

    .. code-block:: vhdl

           null;
         end loop;
    """

    def __init__(self):
        super().__init__(lTokens)
