# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import inside, source
from mhsg.rules.sv_tree import Problem, TreeRule, descendants

ARITHMETIC = ("AddExpression", "SubtractExpression", "MultiplyExpression", "DivideExpression", "ModExpression", "PowerExpression")


class rule_022(TreeRule, structure.Rule):
    """
    This rule checks for arithmetic in the values of a conditional operator in an assignment, such as sel ? a + b : c
    + d, as the STARC guide recommends (2.10.5.5): select the operands first, so one adder serves both. Arithmetic in
    indexes is not checked. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       assign y = sel ? a + b : c + d;

    **Fix**

    .. code-block:: systemverilog

       assign x1 = sel ? a : c;
       assign x2 = sel ? b : d;
       assign y = x1 + x2;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("ConditionalExpression"):
            if not inside(oNode, "ContinuousAssign", "ExpressionStatement"):
                continue
            for oValue in (oNode.left, oNode.right):
                if any(o.kind.name in ARITHMETIC and not inside(o, "ElementSelect") for o in [oValue, *descendants(oValue)]):
                    oToken = oFile.token_at(oValue.getFirstToken())
                    if oToken is not None:
                        yield Problem(oToken, f"Compute {source(oValue)} outside the conditional operator")
