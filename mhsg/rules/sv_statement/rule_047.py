# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule

ARITHMETIC = ("AddExpression", "SubtractExpression", "MultiplyExpression", "DivideExpression", "ModExpression", "PowerExpression")


class rule_047(TreeRule, structure.Rule):
    """
    This rule checks that a line has at most one arithmetic operator, as the STARC guide recommends (2.10.6.6); a + b
    + c, an addition with a carry in, is allowed. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       assign y = a * b + c - d;

    **Fix**

    .. code-block:: systemverilog

       assign p = a * b;
       assign y = p + c - d;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        dLines = {}
        for oNode in oFile.nodes(*ARITHMETIC):
            dLines.setdefault(oFile.line_of(oNode.operatorToken.location.offset), []).append(oNode)
        for _, lNodes in sorted(dLines.items()):
            if len(lNodes) < 2 or (len(lNodes) == 2 and all(o.kind.name == "AddExpression" for o in lNodes)):
                continue
            oFirst = min(lNodes, key=lambda o: o.operatorToken.location.offset)
            oToken = oFile.token_at(oFirst.operatorToken)
            if oToken is not None:
                yield Problem(oToken, f"Write one arithmetic operation per line: this one has {len(lNodes)}")
