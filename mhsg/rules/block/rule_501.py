# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_case import token_case

lTokens = []
lTokens.append(token.block_statement.block_keyword)


class rule_501(token_case):
    """
    This rule checks the **block** keyword has proper case.

    |configuring_uppercase_and_lowercase_rules_link|

    **Violation**

    .. code-block:: vhdl

       block_label : BLOCK is

    **Fix**

    .. code-block:: vhdl

       block_label : block is
    """

    def __init__(self):
        super().__init__(lTokens)
        self.groups.append("case::keyword")
