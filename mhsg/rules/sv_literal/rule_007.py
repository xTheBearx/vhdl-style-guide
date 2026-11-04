# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import inside, vector_literal
from mhsg.rules.sv_tree import Problem, TreeRule, descendants


class rule_007(TreeRule, structure.Rule):
    """
    This rule checks that the constants of the conditions of if statements and conditional operators have a width,
    such as 4'd3 rather than 3 or 'd3, as the STARC guide asks (2.10.3.6). Indexes and unbased fill literals such as
    '0 are not checked. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       if (count == 3) done <= 1'b1;

    **Fix**

    .. code-block:: systemverilog

       if (count == 4'd3) done <= 1'b1;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oPredicate in oFile.nodes("ConditionalPredicate"):
            for oNode in descendants(oPredicate):
                if unsized(oNode) and not inside(oNode, "ElementSelect"):
                    oToken = oFile.token_at(oNode.getFirstToken())
                    if oToken is not None:
                        yield Problem(oToken, f"Give the constant {str(oNode).strip()} a width")


def unsized(oNode):
    """True for a literal without a width, such as 3 or 'd3."""
    if oNode.kind.name == "IntegerLiteralExpression":
        return True
    if oNode.kind.name == "IntegerVectorExpression":
        oLiteral = vector_literal(oNode)
        return oLiteral is not None and oLiteral.size is None
    return False
