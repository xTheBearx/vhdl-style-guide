# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_case import token_case

lTokens = []
lTokens.append(token.variable_declaration.variable_keyword)


class rule_002(token_case):
    """
    This rule checks the **variable** keyword has proper case.

    |configuring_uppercase_and_lowercase_rules_link|

    **Violation**

    .. code-block:: vhdl

       VARIABLE count : integer;

    **Fix**

    .. code-block:: vhdl

       variable count : integer;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.groups.append("case::keyword")
