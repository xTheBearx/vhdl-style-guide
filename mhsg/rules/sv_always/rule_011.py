# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants, elements

ASSIGNMENTS = ("AssignmentExpression", "NonblockingAssignmentExpression")


class rule_011(TreeRule, structure.Rule):
    """
    This rule checks that a combinational always block does not list in its sensitivity list a signal it assigns, as
    the STARC guide asks (2.6.2.2). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       always @(a or y) begin
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
        for oBlock in oFile.nodes("AlwaysBlock"):
            oStatement = oBlock.statement
            if oStatement is None or oStatement.kind.name != "TimingControlStatement":
                continue
            lEvents = [o for o in descendants(oStatement.timingControl) if o.kind.name == "SignalEventExpression"]
            if not lEvents or any(text(o.edge) for o in lEvents):
                continue
            setAssigned = (
                {text(o.left.getFirstToken()) for o in descendants(oStatement.statement) if o.kind.name in ASSIGNMENTS}
                if oStatement.statement is not None
                else set()
            )
            for oEvent in lEvents:
                oFirst = oEvent.expr.getFirstToken() if oEvent.expr is not None else None
                if oFirst is not None and text(oFirst) in setAssigned:
                    oToken = oFile.token_at(oFirst)
                    if oToken is not None:
                        yield Problem(oToken, f"Remove {text(oFirst)}, which the block assigns, from its sensitivity list")
