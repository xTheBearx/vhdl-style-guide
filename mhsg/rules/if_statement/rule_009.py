# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.multiline_alignment_between_tokens import (
    multiline_alignment_between_tokens,
)

lTokenPairs = []
lTokenPairs.append([token.if_statement.if_keyword, token.if_statement.then_keyword])
lTokenPairs.append([token.if_statement.elsif_keyword, token.if_statement.then_keyword])


class rule_009(multiline_alignment_between_tokens):
    """
    This rule checks the alignment of multiline boolean expressions.

    |configuring_multiline_indent_rules_link|

    **Violation**

    .. code-block:: vhdl

       if (a = '0' and b = '1' and
             c = '0') then

    **Fix**

    .. code-block:: vhdl

       if (a = '0' and b = '1' and
           c = '0') then
    """

    def __init__(self):
        super().__init__(lTokenPairs)
        self.bAlignEndTokenWithFirstLine = True
        self.phase = 4
        self.subphase = 2
