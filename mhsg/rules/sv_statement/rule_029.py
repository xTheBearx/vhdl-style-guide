# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import declared_names, inside, source, text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants

ARITHMETIC = ("AddExpression", "SubtractExpression", "MultiplyExpression", "DivideExpression", "ModExpression", "PowerExpression")
RELATIONAL = (
    "EqualityExpression",
    "InequalityExpression",
    "LessThanExpression",
    "LessThanEqualExpression",
    "GreaterThanExpression",
    "GreaterThanEqualExpression",
)
LOGIC = ("LogicalAndExpression", "LogicalOrExpression", "BinaryAndExpression", "BinaryOrExpression", "BinaryXorExpression")


class rule_029(TreeRule, structure.Rule):
    """
    This rule checks for arithmetic, comparisons and logic on signals inside for loops, as the STARC guide recommends
    (2.9.2.1, 2.9.2.2): in a loop, compute only with the loop variable and constants. Indexes are not checked. It is
    disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       for (int i = 0; i < 4; i++) y[i] = a[i] + b;

    **Fix**

    Compute with signals outside the loop, and use only the loop variable and constants in it.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        setSignals = {text(o) for sKind, o in declared_names(oFile) if sKind in ("signal", "port")}
        setDone = set()
        for oLoop in oFile.nodes("ForLoopStatement"):
            for oNode in descendants(oLoop.statement):
                if oNode.kind.name not in ARITHMETIC + RELATIONAL + LOGIC or inside(oNode, "ElementSelect"):
                    continue
                iOffset = oNode.getFirstToken().location.offset
                if iOffset in setDone:
                    continue
                if any(
                    o.kind.name in ("IdentifierName", "IdentifierSelectName") and text(o.identifier) in setSignals
                    for o in (oNode.left, oNode.right)
                    if o is not None
                ):
                    setDone.add(iOffset)
                    oToken = oFile.token_at(oNode.operatorToken)
                    if oToken is not None:
                        yield Problem(oToken, f"Compute {source(oNode)} outside the loop")
