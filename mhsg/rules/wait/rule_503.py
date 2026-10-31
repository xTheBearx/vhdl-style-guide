# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules import token_case as Rule

lTokens = []
lTokens.append(token.timeout_clause.for_keyword)


class rule_503(Rule):
    """
    This rule checks the **for** keyword has proper case.

    |configuring_uppercase_and_lowercase_rules_link|

    **Violation**

    .. code-block:: vhdl

       wait FOR 100 ns;

    **Fix**

    .. code-block:: vhdl

       wait for 100 ns;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.groups.append("case::keyword")
