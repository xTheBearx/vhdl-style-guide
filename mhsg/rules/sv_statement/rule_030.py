# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import inside
from mhsg.rules.sv_tree import Problem, TreeRule, descendants

ARITHMETIC = ("AddExpression", "SubtractExpression", "MultiplyExpression", "DivideExpression", "ModExpression", "PowerExpression")


class rule_030(TreeRule, structure.Rule):
    """
    This rule checks for delays computed with arithmetic in always blocks, such as #(Period / 2), as the STARC guide
    recommends (4.1.6.1): compute clock periods once, as parameters. It is disabled by default; the starc rule set
    enables it.

    **Violation**

    .. code-block:: systemverilog

       always #(Period / 2) clk = ~clk;

    **Fix**

    .. code-block:: systemverilog

       localparam int HalfPeriod = Period / 2;
       always #HalfPeriod clk = ~clk;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oDelay in oFile.nodes("DelayControl"):
            if not inside(oDelay, "AlwaysBlock"):
                continue
            if any(o.kind.name in ARITHMETIC for o in descendants(oDelay)):
                oToken = oFile.token_at(oDelay.getFirstToken())
                if oToken is not None:
                    yield Problem(oToken, "Compute the delay once, as a parameter")
