# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_case import token_case

lTokens = []
lTokens.append(token.index_subtype_definition.range_keyword)


class rule_500(token_case):
    """
    This rule checks the **range** keyword in index subtype definitions has the proper case.

    |configuring_uppercase_and_lowercase_rules_link|

    **Violation**

    .. code-block:: vhdl

       type t_unsigned_array is array(natural RANGE <>) of unsigned;

    **Fix**

    .. code-block:: vhdl

       type t_unsigned_array is array(natural range <>) of unsigned;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.groups.append("case::keyword")
