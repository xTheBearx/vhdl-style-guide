# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_always.rule_012 import clock_events
from mhsg.rules.sv_nodes import integer_of, text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants

NOT = ("UnaryLogicalNotExpression", "UnaryBitwiseNotExpression")


class rule_015(TreeRule, structure.Rule):
    """
    This rule checks that the edge of an asynchronous reset matches the polarity its if tests: negedge for a reset
    tested low, such as if (!rst_ni), and posedge for one tested high, as the STARC guide asks (2.3.1.6). It is
    disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i or posedge rst_ni)
           if (!rst_ni) q <= 1'b0;
           else q <= d;

    **Fix**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i or negedge rst_ni)
           if (!rst_ni) q <= 1'b0;
           else q <= d;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oBlock in oFile.nodes("AlwaysBlock", "AlwaysFFBlock"):
            _, lResets = clock_events(oBlock)
            if not lResets:
                continue
            dTested = {}
            oIf = first_if(oBlock.statement.statement)
            for oPattern in descendants(oIf.predicate):
                if oPattern.kind.name == "ConditionalPattern":
                    dTested.update(polarities(oPattern.expr))
            for oReset in lResets:
                sName = text(oReset.expr.getFirstToken())
                sEdge = text(oReset.edge)
                if sName in dTested and (sEdge == "posedge") != dTested[sName]:
                    oToken = oFile.token_at(oReset.edge)
                    if oToken is not None:
                        sLevel = "high" if dTested[sName] else "low"
                        yield Problem(oToken, f"The reset {sName} is tested {sLevel}: use {'posedge' if dTested[sName] else 'negedge'}")


def first_if(oStatement):
    """The first statement of an always block, after its event control, if it is an if statement, else None."""
    while oStatement is not None and oStatement.kind.name == "SequentialBlockStatement":
        lItems = [o for o in oStatement.items if hasattr(o, "kind") and o.kind.name.endswith("Statement")]
        oStatement = lItems[0] if lItems else None
    return oStatement if oStatement is not None and oStatement.kind.name == "ConditionalStatement" else None


def polarities(oExpression, bHigh=True):
    """The names a simple condition tests, each with True if tested high, such as {"rst_ni": False} for !rst_ni."""
    sKind = oExpression.kind.name
    if sKind == "ParenthesizedExpression":
        return polarities(oExpression.expression, bHigh)
    if sKind in NOT:
        return polarities(oExpression.operand, not bHigh)
    if sKind in ("IdentifierName", "IdentifierSelectName"):
        return {text(oExpression.identifier): bHigh}
    if sKind in ("EqualityExpression", "InequalityExpression", "CaseEqualityExpression", "CaseInequalityExpression"):
        oName, oValue = oExpression.left, oExpression.right
        if integer_of(oName) is not None:
            oName, oValue = oValue, oName
        iValue = integer_of(oValue)
        if iValue is None or oName.kind.name not in ("IdentifierName", "IdentifierSelectName"):
            return {}
        bEqual = sKind in ("EqualityExpression", "CaseEqualityExpression")
        return {text(oName.identifier): bHigh == (bEqual == (iValue != 0))}
    if sKind == "LogicalOrExpression":
        dReturn = polarities(oExpression.left, bHigh)
        dReturn.update(polarities(oExpression.right, bHigh))
        return dReturn
    return {}
