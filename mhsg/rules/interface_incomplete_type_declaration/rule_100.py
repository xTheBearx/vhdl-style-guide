# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.whitespace_before_token import Rule

lTokens = []
lTokens.append(token.interface_incomplete_type_declaration.is_keyword)


class rule_100(Rule):
    """
    This rule checks for a single space before the **is** keyword.

    |configuring_whitespace_rules_link|

    **Violation**

    .. code-block:: vhdl

       type t_data    is private;

    **Fix**

    .. code-block:: vhdl

       type t_data is private;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.number_of_spaces = 1
