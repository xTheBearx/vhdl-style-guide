# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules import token_case

lTokens = []
lTokens.append(token.protected_type_declaration.end_keyword)


class rule_501(token_case):
    """
    This rule checks the **end** keyword in **end protected** has proper case.

    |configuring_uppercase_and_lowercase_rules_link|

    **Violation**

    .. code-block:: vhdl

       END protected sharedcounter;

    **Fix**

    .. code-block:: vhdl

       end protected sharedcounter;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.groups.append("case::keyword")
