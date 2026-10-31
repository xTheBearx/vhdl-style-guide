# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_case import token_case

lTokens = []
lTokens.append(token.block_statement.end_block_keyword)


class rule_505(token_case):
    """
    This rule checks the **block** keyword in the **end block** has proper case.

    |configuring_uppercase_and_lowercase_rules_link|

    **Violation**

    .. code-block:: vhdl

       end BLOCK block_label;

    **Fix**

    .. code-block:: vhdl

       end block block_label;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.groups.append("case::keyword")
