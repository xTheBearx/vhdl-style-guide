# -*- coding: utf-8 -*-

from mhsg.rules.sv_spacing import Rule, kind, node


class rule_010(Rule):
    """
    This rule checks for no space between ++ or -- and its operand, as Verible's formatter does.

    **Violation**

    .. code-block:: systemverilog

       count ++;

    **Fix**

    .. code-block:: systemverilog

       count++;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Remove space around ++ or --"

    def spacing(self, oLeft, oRight):
        if kind(oRight) in ("DoublePlus", "DoubleMinus") and node(oRight) in ("PostincrementExpression", "PostdecrementExpression"):
            return (0, True)
        if kind(oLeft) in ("DoublePlus", "DoubleMinus") and node(oLeft) in ("PreincrementExpression", "PredecrementExpression"):
            return (0, True)
        return None
