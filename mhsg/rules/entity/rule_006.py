# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_case import token_case

lTokens = []
lTokens.append(token.entity_declaration.is_keyword)


class rule_006(token_case):
    """
    This rule checks the **is** keyword has proper case in the entity declaration.

    |configuring_uppercase_and_lowercase_rules_link|

    **Violation**

    .. code-block:: vhdl

       entity fifo IS

    **Fix**

    .. code-block:: vhdl

       entity fifo is
    """

    def __init__(self):
        super().__init__(lTokens)
        self.groups.append("case::keyword")
