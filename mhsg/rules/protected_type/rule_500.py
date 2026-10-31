# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_case import token_case

lTokens = []
lTokens.append(token.protected_type_declaration.protected_keyword)


class rule_500(token_case):
    """
    This rule checks the **protected** keyword has proper case.

    |configuring_uppercase_and_lowercase_rules_link|

    **Violation**

    .. code-block:: vhdl

       type sharedcounter is PROTECTED

    **Fix**

    .. code-block:: vhdl

       type sharedcounter is protected
    """

    def __init__(self):
        super().__init__(lTokens)
        self.groups.append("case::keyword")
