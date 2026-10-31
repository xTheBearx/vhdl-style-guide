# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.whitespace_after_token import Rule

lTokens = []
lTokens.append(token.range_constraint.range_keyword)


class rule_101(Rule):
    """
    This rule checks for a single space after the **range** keyword.

    |configuring_whitespace_rules_link|

    **Violation**

    .. code-block:: vhdl

      subtype my_range is natural range     0 to 7;

    **Fix**

    .. code-block:: vhdl

      subtype my_range is natural range 0 to 7;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.number_of_spaces = 1
