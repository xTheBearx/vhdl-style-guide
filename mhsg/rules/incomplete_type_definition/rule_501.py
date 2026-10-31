# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.token_case import token_case

lTokens = []
lTokens.append(token.incomplete_type_definition.range_keyword)


class rule_501(token_case):
    """
    This rule checks the **range** keyword has proper case.

    |configuring_uppercase_and_lowercase_rules_link|

    **Violation**

    .. code-block:: vhdl

       type t_data is RANGE <>;

    **Fix**

    .. code-block:: vhdl

       type t_data is range <>;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.groups.append("case::keyword")
