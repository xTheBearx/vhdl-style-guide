# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules import token_case as Rule

lTokens = []
lTokens.append(token.condition_clause.until_keyword)


class rule_502(Rule):
    """
    This rule checks the **until** keyword has proper case.

    |configuring_uppercase_and_lowercase_rules_link|

    **Violation**

    .. code-block:: vhdl

       wait UNTIL rising_edge(clk);

    **Fix**

    .. code-block:: vhdl

       wait until rising_edge(clk);
    """

    def __init__(self):
        super().__init__(lTokens)
        self.groups.append("case::keyword")
