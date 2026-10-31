# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_indent import token_indent as Rule

lTokens = []
lTokens.append(token.next_statement.label)


class rule_301(Rule):
    """
    This rule checks the indentation of the label.

    **Violation**

    .. code-block:: vhdl

         next_label : next when condition;
         end function;

    **Fix**

    .. code-block:: vhdl

           next_label : next when condition;
         end function;
    """

    def __init__(self):
        super().__init__(lTokens)
