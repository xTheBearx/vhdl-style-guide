# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_case import token_case

lTokens = []
lTokens.append(token.attribute_specification.of_keyword)


class rule_502(token_case):
    """
    This rule checks the **of** keyword has proper case.

    |configuring_uppercase_and_lowercase_rules_link|

    **Violation**

    .. code-block:: vhdl

       attribute coordinate OF comp_1 : component is (0.0, 17.5);

    **Fix**

    .. code-block:: vhdl

       attribute coordinate of comp_1 : component is (0.0, 17.5);
    """

    def __init__(self):
        super().__init__(lTokens)
        self.groups.append("case::keyword")
