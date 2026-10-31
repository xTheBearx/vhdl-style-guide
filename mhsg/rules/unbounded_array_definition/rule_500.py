# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_case import token_case

lTokens = []
lTokens.append(token.unbounded_array_definition.array_keyword)


class rule_500(token_case):
    """
    This rule checks the **array** keyword has proper case.

    |configuring_uppercase_and_lowercase_rules_link|

    **Violation**

    .. code-block:: vhdl

       type t_u_array_unconstrained is ARRAY(natural range <>) of unsigned;

    **Fix**

    .. code-block:: vhdl

       type t_u_array_unconstrained is array(natural range <>) of unsigned;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.groups.append("case::keyword")
