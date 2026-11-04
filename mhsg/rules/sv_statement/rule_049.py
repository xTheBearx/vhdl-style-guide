# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import inside, text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants


class rule_049(TreeRule, structure.Rule):
    """
    This rule checks that test stimulus is not assigned right at a clock edge, after an event control such as
    @(posedge clk) without a delay, as the STARC guide recommends (4.1.3.1, 4.1.3.2), in initial blocks and tasks. It
    is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       @(posedge clk);
       data = 8'h55;

    **Fix**

    .. code-block:: systemverilog

       @(posedge clk);
       #1 data = 8'h55;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("TimingControlStatement"):
            if not inside(oNode, "InitialBlock", "TaskDeclaration") or oNode.timingControl.kind.name not in ("EventControlWithExpression", "EventControl"):
                continue
            if not any(o.kind.name == "SignalEventExpression" and text(o.edge) for o in descendants(oNode.timingControl)):
                continue
            oNext = oNode.statement
            if oNext is not None and oNext.kind.name == "EmptyStatement":
                oNext = following(oNode)
            if (
                oNext is not None
                and oNext.kind.name == "ExpressionStatement"
                and oNext.expr is not None
                and oNext.expr.kind.name in ("AssignmentExpression", "NonblockingAssignmentExpression")
            ):
                oToken = oFile.token_at(oNext.getFirstToken())
                if oToken is not None:
                    yield Problem(oToken, "Offset the stimulus from the clock edge with a delay")


def following(oStatement):
    """The statement after a statement in its block, or None."""
    oParent = oStatement.parent
    lItems = [o for o in getattr(oParent, "items", None) or [] if hasattr(o, "kind")] if oParent is not None else []
    lOffsets = [o.getFirstToken().location.offset for o in lItems]
    iOffset = oStatement.getFirstToken().location.offset
    return lItems[lOffsets.index(iOffset) + 1] if iOffset in lOffsets and lOffsets.index(iOffset) + 1 < len(lItems) else None
