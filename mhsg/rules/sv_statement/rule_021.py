# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import source
from mhsg.rules.sv_tree import Problem, TreeRule

ARITHMETIC = ("AddExpression", "SubtractExpression", "MultiplyExpression", "DivideExpression", "ModExpression", "PowerExpression")


class rule_021(TreeRule, structure.Rule):
    """
    This rule checks that an expression with two or more arithmetic operators, such as a + b - c, has parentheses
    showing their order, as the STARC guide recommends (2.10.1.3). It is disabled by default; the starc rule set
    enables it.

    **Violation**

    .. code-block:: systemverilog

       assign sum = a + b - c;

    **Fix**

    .. code-block:: systemverilog

       assign sum = (a + b) - c;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes(*ARITHMETIC):
            if oNode.parent is not None and oNode.parent.kind.name in ARITHMETIC:
                continue
            if any(o is not None and o.kind.name in ARITHMETIC for o in (oNode.left, oNode.right)):
                oToken = oFile.token_at(oNode.operatorToken)
                if oToken is not None:
                    yield Problem(oToken, f"Add parentheses to {source(oNode)}")
