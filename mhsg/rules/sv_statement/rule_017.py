# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import has_x_or_z
from mhsg.rules.sv_tree import Problem, TreeRule, descendants


class rule_017(TreeRule, structure.Rule):
    """
    This rule checks that the enable of a tri-state buffer, the condition of a conditional operator with a z value,
    is a plain signal, not an expression, as the STARC guide recommends (2.5.1.2). It is disabled by default; the
    starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       assign bus = (oe & sel) ? data : 'z;

    **Fix**

    .. code-block:: systemverilog

       assign enable = oe & sel;
       assign bus = enable ? data : 'z;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("ConditionalExpression"):
            if not (high_impedance(oNode.left) or high_impedance(oNode.right)):
                continue
            for oPattern in descendants(oNode.predicate):
                if oPattern.kind.name == "ConditionalPattern":
                    oCondition = oPattern.expr
                    while oCondition.kind.name == "ParenthesizedExpression":
                        oCondition = oCondition.expression
                    if oCondition.kind.name not in ("IdentifierName", "IdentifierSelectName"):
                        oToken = oFile.token_at(oPattern.getFirstToken())
                        if oToken is not None:
                            yield Problem(oToken, "Use a plain signal as the enable of the tri-state buffer")
                    break


def high_impedance(oNode):
    """True for a literal with z digits, such as 8'bz or 'z."""
    return has_x_or_z(oNode) and "z" in str(oNode).lower()
