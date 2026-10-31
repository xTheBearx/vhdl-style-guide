# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.whitespace_after_token import Rule

lTokens = []
lTokens.append(token.incomplete_type_definition.of_keyword)


class rule_101(Rule):
    """
    This rule checks for a single space after the **of** keyword.

    |configuring_whitespace_rules_link|

    **Violation**

    .. code-block:: vhdl

       type t_data is file of    type is private;

    **Fix**

    .. code-block:: vhdl

       type t_data is file of type is private;
    """

    def __init__(self):
        super().__init__(lTokens)
