# -*- coding: utf-8 -*-

from mhsg import parser
from mhsg.rules.sv_spacing import Rule, kind


class rule_016(Rule):
    """
    This rule checks for no space after an opening parenthesis and before a closing one, as Verible's formatter does.
    A parenthesis at the end or the start of a line, or followed by a comment, is not checked.

    **Violation**

    .. code-block:: systemverilog

       assign y = ( a & b ) | c;
       sub u_sub ( .a(a), .y(y) );

    **Fix**

    .. code-block:: systemverilog

       assign y = (a & b) | c;
       sub u_sub (.a(a), .y(y));
    """

    def __init__(self):
        super().__init__()
        self.solution = "Remove the space inside the parentheses"

    def spacing(self, oLeft, oRight):
        if isinstance(oRight, parser.comment):
            return None
        if kind(oLeft) == "OpenParenthesis" or kind(oRight) == "CloseParenthesis":
            return (0, True)
        return None
