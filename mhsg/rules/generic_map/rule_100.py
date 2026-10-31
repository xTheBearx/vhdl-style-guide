# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.whitespace_before_tokens_in_between_tokens import Rule

lTokens = []
lTokens.append(token.association_element.assignment)

oStart = token.generic_map_aspect.open_parenthesis
oEnd = token.generic_map_aspect.close_parenthesis


class rule_100(Rule):
    """
    This rules checks for whitespace before the assignment operator.

    |configuring_whitespace_rules_link|

    **Violation**

    .. code-block:: vhdl

       generic map (
         WIDTH=> 32,
         DEPTH=> 512
       );

    **Fix**

    .. code-block:: vhdl

       generic map (
         WIDTH => 32,
         DEPTH => 512
       );
    """

    def __init__(self):
        super().__init__(lTokens, oStart, oEnd)
        self.number_of_spaces = ">=1"
