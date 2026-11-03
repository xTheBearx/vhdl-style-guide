# -*- coding: utf-8 -*-

from mhsg import parser
from mhsg.rules.sv_spacing import Rule


class rule_015(Rule):
    """
    This rule checks for at least **spaces** spaces, 2 by default, between code and a comment at the end of its
    line, as Verible's formatter does.

    **Violation**

    .. code-block:: systemverilog

       logic valid; // the data is valid

    **Fix**

    .. code-block:: systemverilog

       logic valid;  // the data is valid
    """

    def __init__(self):
        super().__init__()
        self.solution = "Add spaces before the comment"
        self.spaces = 2
        self.configuration.append("spaces")

    def spacing(self, oLeft, oRight):
        if isinstance(oRight, parser.comment):
            return (self.spaces, False)
        return None
