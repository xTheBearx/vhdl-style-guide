# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_015(TreeRule, structure.Rule):
    """
    This rule checks that delays are non-negative integers, not real or negative numbers, as the STARC guide asks
    (2.3.1.5). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       #(1.5) q = d;

    **Fix**

    .. code-block:: systemverilog

       #2 q = d;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oDelay in oFile.nodes("DelayControl"):
            oValue = oDelay.delayValue
            while oValue is not None and oValue.kind.name == "ParenthesizedExpression":
                oValue = oValue.expression
            if oValue is not None and oValue.kind.name in ("RealLiteralExpression", "UnaryMinusExpression"):
                oToken = oFile.token_at(oDelay.getFirstToken())
                if oToken is not None:
                    yield Problem(oToken, "Use a non-negative integer delay")
