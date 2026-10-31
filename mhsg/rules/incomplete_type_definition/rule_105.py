# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.whitespace_after_token import Rule

lTokens = []
lTokens.append(token.incomplete_type_definition.units_keyword)


class rule_105(Rule):
    """
    This rule checks for a single space after the **units** keyword.

    |configuring_whitespace_rules_link|

    **Violation**

    .. code-block:: vhdl

       type t_data is units    <>;

    **Fix**

    .. code-block:: vhdl

       type t_data is units <>;
    """

    def __init__(self):
        super().__init__(lTokens)
