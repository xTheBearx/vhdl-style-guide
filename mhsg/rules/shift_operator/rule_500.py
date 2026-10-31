# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_case import token_case

lTokens = []
lTokens.append(token.shift_operator.sll)
lTokens.append(token.shift_operator.srl)
lTokens.append(token.shift_operator.sla)
lTokens.append(token.shift_operator.sra)
lTokens.append(token.shift_operator.rol)
lTokens.append(token.shift_operator.ror)


class rule_500(token_case):
    """
    This rule checks shift operators have proper case.

    |configuring_uppercase_and_lowercase_rules_link|

    **Violation**

    .. code-block:: vhdl

       a <= b SLL c;

    **Fix**

    .. code-block:: vhdl

       a <= b sll c;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.groups.append("case::keyword")
