# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.whitespace_after_token import Rule

lTokens = []
lTokens.append(token.incomplete_type_definition.range_keyword)


class rule_104(Rule):
    """
    This rule checks for a single space after the **range** keyword.

    |configuring_whitespace_rules_link|

    **Violation**

    .. code-block:: vhdl

       type t_data is range    <>;

    **Fix**

    .. code-block:: vhdl

       type t_data is range <>;
    """

    def __init__(self):
        super().__init__(lTokens)
