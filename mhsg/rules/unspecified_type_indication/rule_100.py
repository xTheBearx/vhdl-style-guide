# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.whitespace_after_token import Rule

lTokens = []
lTokens.append(token.unspecified_type_indication.type_keyword)


class rule_100(Rule):
    """
    This rule checks for a single space after the **type** keyword.

    |configuring_whitespace_rules_link|

    **Violation**

    .. code-block:: vhdl

       type t_data is access type    is private;

    **Fix**

    .. code-block:: vhdl

       type t_data is access type is private;
    """

    def __init__(self):
        super().__init__(lTokens)
