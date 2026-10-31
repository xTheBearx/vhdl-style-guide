# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_case import token_case

lTokens = []
lTokens.append(token.protected_type_body.end_keyword)


class rule_502(token_case):
    """
    This rule checks the **end** keyword in **end protected body** has proper case.

    |configuring_uppercase_and_lowercase_rules_link|

    **Violation**

    .. code-block:: vhdl

       END protected body sharedcounter;

    **Fix**

    .. code-block:: vhdl

       end protected body sharedcounter;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.groups.append("case::keyword")
