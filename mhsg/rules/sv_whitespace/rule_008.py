# -*- coding: utf-8 -*-

from mhsg import parser
from mhsg.rules.sv_spacing import Rule, is_binary_operator, kind


class rule_008(Rule):
    """
    This rule checks for at least one space around binary and assignment operators and the ? and : of a
    conditional expression, except in the brackets of a select or a dimension, as Verible's formatter does.

    **Violation**

    .. code-block:: systemverilog

       assign sum=a+b;

    **Fix**

    .. code-block:: systemverilog

       assign sum = a + b;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Add a space around the operator"

    def spacing(self, oLeft, oRight):
        # A comma separating events, as in @(a, b), is spaced as a comma
        if isinstance(oRight, parser.comment) or kind(oRight) == "Comma":
            return None
        if is_binary_operator(oLeft) or is_binary_operator(oRight):
            return (1, False)
        return None
