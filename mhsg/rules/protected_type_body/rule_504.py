# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules import token_case

lTokens = []
lTokens.append(token.protected_type_body.end_body_keyword)


class rule_504(token_case):
    """
    This rule checks the **body** keyword in **end protected body** has proper case.

    |configuring_uppercase_and_lowercase_rules_link|

    **Violation**

    .. code-block:: vhdl

       end protected BODY sharedcounter;

    **Fix**

    .. code-block:: vhdl

       end protected body sharedcounter;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.groups.append("case::keyword")
