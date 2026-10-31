# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.whitespace_after_token import Rule

lTokens = []
lTokens.append(token.variable_declaration.shared_keyword)


class rule_101(Rule):
    """
    This rule checks for a single space after the **shared** keyword.

    |configuring_whitespace_rules_link|

    **Violation**

    .. code-block:: vhdl

       shared    variable size : integer;

    **Fix**

    .. code-block:: vhdl

       shared variable size : integer;
    """

    def __init__(self):
        super().__init__(lTokens)
