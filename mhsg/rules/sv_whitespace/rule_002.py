# -*- coding: utf-8 -*-

from mhsg import parser
from mhsg.rules.sv_spacing import Rule, kind


class rule_002(Rule):
    """
    This rule checks for at least one space after a comma, as Verible's formatter does.

    **Violation**

    .. code-block:: systemverilog

       foo(a,b);

    **Fix**

    .. code-block:: systemverilog

       foo(a, b);
    """

    def __init__(self):
        super().__init__()
        self.solution = "Add a space after comma"

    def spacing(self, oLeft, oRight):
        # An empty argument, as in f(a, , b), keeps no space before its comma
        if kind(oLeft) == "Comma" and kind(oRight) != "Comma" and not isinstance(oRight, parser.comment):
            return (1, False)
        return None
