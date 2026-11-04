# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule

TARGETS = (
    "NonblockingAssignmentExpression",
    "AssignmentExpression",
    "EqualityExpression",
    "InequalityExpression",
    "LessThanExpression",
    "LessThanEqualExpression",
    "GreaterThanExpression",
    "GreaterThanEqualExpression",
)
SKIP = (
    "ElementSelect",
    "VariableDimension",
    "DelayControl",
    "ConditionalPredicate",
    "ParameterDeclaration",
    "LocalParamDeclaration",
    "ForVariableDeclaration",
    "InvocationExpression",
    "CastExpression",
)


class rule_008(TreeRule, structure.Rule):
    """
    This rule checks that the numbers assigned to signals and compared with them are written with a base, such as 'd5
    or 8'h1F rather than 5, as the STARC guide recommends (2.10.3.5). Indexes, dimensions, loop headers, delays,
    replication counts and the conditions sv_literal_007 checks are not checked. It is disabled by default; the starc
    rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       count <= 5;

    **Fix**

    .. code-block:: systemverilog

       count <= 'd5;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("IntegerLiteralExpression"):
            if checked(oNode):
                oToken = oFile.token_at(oNode.getFirstToken())
                if oToken is not None:
                    yield Problem(oToken, f"Write {text(oNode.literal)} with a base, such as 'd{text(oNode.literal)}")


def checked(oNode):
    """True for a number on the right of an assignment or in a comparison, outside the places the rule skips."""
    oChild, oParent = oNode, oNode.parent
    bTarget = False
    while oParent is not None:
        sKind = oParent.kind.name
        if sKind in SKIP or (sKind == "MultipleConcatenationExpression" and oChild is oParent.expression):
            return False
        if sKind in TARGETS and not (sKind.endswith("AssignmentExpression") and oChild is oParent.left):
            bTarget = True
        if sKind.endswith("Statement") or sKind.endswith("Declaration") or sKind == "ContinuousAssign":
            return bTarget and sKind != "ForLoopStatement"
        oChild, oParent = oParent, oParent.parent
    return bTarget
