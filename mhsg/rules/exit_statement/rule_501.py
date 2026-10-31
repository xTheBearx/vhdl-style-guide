# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_case import token_case as Rule

lTokens = []
lTokens.append(token.exit_statement.when_keyword)


class rule_501(Rule):
    """
    This rule checks the **when** keyword has proper case.

    |configuring_uppercase_and_lowercase_rules_link|

    **Violation**

    .. code-block:: vhdl

       exit WHEN condition;

    **Fix**

    .. code-block:: vhdl

       exit when condition;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.groups.append("case::keyword")
