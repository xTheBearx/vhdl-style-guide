# -*- coding: utf-8 -*-

from mhsg import token
from mhsg.rules.multiline_alignment_between_tokens import (
    multiline_alignment_between_tokens as Rule,
)

lTokenPairs = []
lTokenPairs.append([token.signal_declaration.signal_keyword, token.signal_declaration.semicolon])


class rule_400(Rule):
    """
    This rule checks alignment of multiline constraints in signal declarations.

    |configuring_multiline_indent_rules_link|

    **Violation**

    .. code-block:: vhdl

       signal sig_a : my_record(
                element1(7 downto 0),
       element2(3 downto 0)
               );

    **Fix**

    .. code-block:: vhdl

       signal sig_a : my_record(
           element1(7 downto 0),
           element2(3 downto 0)
         );
    """

    def __init__(self):
        super().__init__(lTokenPairs)
        self.phase = 5
        # The continuation lines of a constraint move the := after it, so they are aligned before the := of the
        # declarations are (declarative_part_400, subphase 3); those of a default value hang off the :=, so they are
        # aligned again after
        self.subphase = 2
        self.fix_again_in_subphase = 4
        self.bIgnoreStartParen = True
        self.bConstraint = True
