# -*- coding: utf-8 -*-

from mhsg.rules.sv_spacing import Rule, kind


class rule_001(Rule):
    """
    This rule checks for no space before a comma, as Verible's formatter does.

    **Violation**

    .. code-block:: systemverilog

       foo(a , b);

    **Fix**

    .. code-block:: systemverilog

       foo(a, b);
    """

    def __init__(self):
        super().__init__()
        self.solution = "Remove space before comma"

    def spacing(self, oLeft, oRight):
        if kind(oRight) == "Comma":
            return (0, True)
        return None
