# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.split_line_at_token_if_on_same_line_as_token_if_token_pair_are_not_on_the_same_line import (
    split_line_at_token_if_on_same_line_as_token_if_token_pair_are_not_on_the_same_line,
)

oToken = token.enumeration_type_definition.enumeration_literal

oSameLineToken = token.enumeration_type_definition.open_parenthesis

lTokenPair = [token.full_type_declaration.type_keyword, token.full_type_declaration.semicolon]


class rule_009(split_line_at_token_if_on_same_line_as_token_if_token_pair_are_not_on_the_same_line):
    """
    This rule checks for an enumerate type after the open parenthesis on multiline enumerated types.

    **Violation**

    .. code-block:: vhdl

       type state_machine is (idle,
         write,
         read,
         done
       );

    **Fix**

    .. code-block:: vhdl

       type state_machine is (
         idle,
         write,
         read,
         done
       );
    """

    def __init__(self):
        super().__init__(oToken, oSameLineToken, lTokenPair)
        self.solution = "Move enumerated type to the next line."
