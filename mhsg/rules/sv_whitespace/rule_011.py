# -*- coding: utf-8 -*-

from mhsg.rules.sv_spacing import Rule, field, kind, node


class rule_011(Rule):
    """
    This rule checks for no space between the name of a function, task or system task and its argument list, as
    Verible's formatter does.

    **Violation**

    .. code-block:: systemverilog

       $display ("done");

    **Fix**

    .. code-block:: systemverilog

       $display("done");
    """

    def __init__(self):
        super().__init__()
        self.solution = "Remove space before ("

    def spacing(self, oLeft, oRight):
        if kind(oRight) == "OpenParenthesis" and node(oRight) == "ArgumentList" and field(oRight) == "openParen":
            return (0, True)
        return None
