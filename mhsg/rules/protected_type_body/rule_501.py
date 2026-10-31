# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules import token_case

lTokens = []
lTokens.append(token.protected_type_body.body_keyword)


class rule_501(token_case):
    """
    This rule checks the **body** keyword in **protected body** has proper case.

    |configuring_uppercase_and_lowercase_rules_link|

    **Violation**

    .. code-block:: vhdl

       type sharedcounter is protected BODY

    **Fix**

    .. code-block:: vhdl

       type sharedcounter is protected body
    """

    def __init__(self):
        super().__init__(lTokens)
        self.groups.append("case::keyword")
