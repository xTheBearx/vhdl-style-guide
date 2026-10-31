# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_case import token_case

lTokens = []
lTokens.append(token.instantiated_unit.entity_keyword)


class rule_027(token_case):
    """
    This rule checks the **entity** keyword has proper case in direct instantiations.

    |configuring_uppercase_and_lowercase_rules_link|

    **Violation**

    .. code-block:: vhdl

       INSTANCE_NAME : ENTITY library.ENTITY_NAME

    **Fix**

    .. code-block:: vhdl

       INSTANCE_NAME : entity library.ENTITY_NAME
    """

    def __init__(self):
        super().__init__(lTokens)
        self.groups.append("case::keyword")
