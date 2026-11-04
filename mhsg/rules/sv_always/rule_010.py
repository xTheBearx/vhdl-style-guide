# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import declared_names, text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants

LITERALS = ("IntegerLiteralExpression", "IntegerVectorExpression", "UnbasedUnsizedLiteralExpression")


class rule_010(TreeRule, structure.Rule):
    """
    This rule checks for constants, such as 1'b1 or a parameter, in the sensitivity list of an always block, as the
    STARC guide asks (2.2.2.2). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       always @(a or 1'b1) begin
           y = a;
       end

    **Fix**

    .. code-block:: systemverilog

       always @(a) begin
           y = a;
       end
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        setConstants = {text(oName) for sKind, oName in declared_names(oFile) if sKind in ("parameter", "localparam")}
        for oBlock in oFile.nodes("AlwaysBlock"):
            oStatement = oBlock.statement
            if oStatement is None or oStatement.kind.name != "TimingControlStatement":
                continue
            for oEvent in descendants(oStatement.timingControl):
                if oEvent.kind.name != "SignalEventExpression" or oEvent.expr is None:
                    continue
                bConstant = oEvent.expr.kind.name in LITERALS or (oEvent.expr.kind.name == "IdentifierName" and text(oEvent.expr.identifier) in setConstants)
                if bConstant:
                    oToken = oFile.token_at(oEvent.expr.getFirstToken())
                    if oToken is not None:
                        yield Problem(oToken, "Remove the constant from the sensitivity list")
