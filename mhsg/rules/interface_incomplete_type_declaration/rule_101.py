# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.whitespace_after_token import Rule

lTokens = []
lTokens.append(token.interface_incomplete_type_declaration.is_keyword)


class rule_101(Rule):
    """
    This rule checks for a single space after the **is** keyword.

    |configuring_whitespace_rules_link|

    **Violation**

    .. code-block:: vhdl

       type t_data is    private;

    **Fix**

    .. code-block:: vhdl

       type t_data is private;
    """

    def __init__(self):
        super().__init__(lTokens)
