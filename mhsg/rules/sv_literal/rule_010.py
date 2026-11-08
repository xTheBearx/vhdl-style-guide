# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import integer_of, source
from mhsg.rules.sv_tree import Problem, TreeRule

SKIP = (
    "ParameterDeclaration",
    "ParameterValueAssignment",
    "VariableDimension",
    "ElementSelect",
    "DelayControl",
    "TypedefDeclaration",
    "AttributeSpec",
    "CastExpression",
)


class rule_010(TreeRule, structure.Rule):
    """
    This rule checks for numbers other than 0 and 1 in the code, as the STARC guide recommends (3.2.2.1, 4.1.2.1):
    name them with parameters. Parameter declarations, parameter values given to an instance, as in #(.WIDTH(12)) or
    #(12), dimensions, indexes, delays, replication counts, loop headers and the values of case items, as in 3'd5:,
    are not checked. The statements of the case items are checked like any other, default included. It is disabled
    by default; the starc and do254 rule sets enable it.

    **Violation**

    .. code-block:: systemverilog

       if (count == 8'd200) done <= 1'b1;

    **Fix**

    .. code-block:: systemverilog

       localparam logic [7:0] Limit = 8'd200;
       if (count == Limit) done <= 1'b1;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("IntegerLiteralExpression", "IntegerVectorExpression"):
            iValue = integer_of(oNode)
            if iValue is None or iValue in (0, 1) or not checked(oNode):
                continue
            oToken = oFile.token_at(oNode.getFirstToken())
            if oToken is not None:
                yield Problem(oToken, f"Name {source(oNode)} with a parameter")


def checked(oNode):
    """True for a number outside the places the rule skips."""
    oChild, oParent = oNode, oNode.parent
    while oParent is not None:
        if oParent.kind.name in SKIP or (oParent.kind.name == "MultipleConcatenationExpression" and oChild is oParent.expression):
            return False
        if oParent.kind.name == "StandardCaseItem" and oChild is not oParent.clause:
            # The values of the item, not its statement
            return False
        if oParent.kind.name == "ForLoopStatement":
            # The header of the loop, not its body
            return oChild.getFirstToken().location.offset == oParent.statement.getFirstToken().location.offset
        oChild, oParent = oParent, oParent.parent
    return True
