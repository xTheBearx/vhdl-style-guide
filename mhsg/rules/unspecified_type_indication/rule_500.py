# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_case import token_case

lTokens = []
lTokens.append(token.unspecified_type_indication.type_keyword)


class rule_500(token_case):
    """
    This rule checks the **type** keyword has proper case.

    |configuring_uppercase_and_lowercase_rules_link|

    **Violation**

    .. code-block:: vhdl

       type t_data is access TYPE is private;

    **Fix**

    .. code-block:: vhdl

       type t_data is access type is private;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.groups.append("case::keyword")
