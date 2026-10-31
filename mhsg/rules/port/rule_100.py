# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.whitespace_before_token import Rule

lTokens = []
lTokens.append(token.simple_mode_indication.assignment)


class rule_100(Rule):
    """
    This rule checks for at least a single space before the assignment.

    |configuring_whitespace_rules_link|

    **Violation**

    .. code-block:: vhdl

       I_WIDTH : in integer:= 32;

    **Fix**

    .. code-block:: vhdl

       I_WIDTH : in integer := 32;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.number_of_spaces = ">=1"
