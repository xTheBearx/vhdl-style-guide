# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.insert_carriage_return_after_token_if_it_is_not_followed_by_a_comment_when_between_tokens import (
    insert_carriage_return_after_token_if_it_is_not_followed_by_a_comment_when_between_tokens as Rule,
)

lTokens = []
lTokens.append(token.association_list.comma)

lTokenPairs = []
lTokenPairs.append([token.generic_map_aspect.open_parenthesis, token.generic_map_aspect.close_parenthesis])


class rule_010(Rule):
    """
    This rule checks multiple generic assignments on the same line.

    .. NOTE:: This rule is disabled by default, because short generic maps such as :code:`generic map (A => 1, B => 2)` are common.
       It can be enabled to match port_map_009.

    **Violation**

    .. code-block:: vhdl

       generic map (
         G_WIDTH => 8, G_DEPTH => 16,
         G_RESET => '0'
       )

    **Fix**

    .. code-block:: vhdl

       generic map (
         G_WIDTH => 8,
         G_DEPTH => 16,
         G_RESET => '0'
       )
    """

    def __init__(self):
        super().__init__(lTokens, lTokenPairs)
        self.solution = "Move multiple generic assignments to their own lines."
        self.disable = True
