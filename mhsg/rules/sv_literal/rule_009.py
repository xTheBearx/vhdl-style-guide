# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import source
from mhsg.rules.sv_tree import Problem, TreeRule

ASSIGNMENTS = ("NonblockingAssignmentExpression", "AssignmentExpression")
LITERALS = ("IntegerLiteralExpression", "IntegerVectorExpression", "UnbasedUnsizedLiteralExpression")


class rule_009(TreeRule, structure.Rule):
    """
    This rule checks for negative constants assigned to signals, such as count <= -1, as the STARC guide asks
    (2.10.4.5, 2.10.4.6). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       count <= -1;

    **Fix**

    .. code-block:: systemverilog

       count <= '1;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes(*ASSIGNMENTS):
            oRight = oNode.right
            while oRight is not None and oRight.kind.name == "ParenthesizedExpression":
                oRight = oRight.expression
            if oRight is not None and oRight.kind.name == "UnaryMinusExpression" and oRight.operand.kind.name in LITERALS:
                oToken = oFile.token_at(oRight.getFirstToken())
                if oToken is not None:
                    yield Problem(oToken, f"Do not assign the negative value {source(oRight)}")
