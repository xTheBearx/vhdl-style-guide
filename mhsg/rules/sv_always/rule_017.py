# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_always.rule_012 import clock_events
from mhsg.rules.sv_nodes import source
from mhsg.rules.sv_tree import Problem, TreeRule, descendants

ASSIGNMENTS = ("NonblockingAssignmentExpression", "AssignmentExpression")


class rule_017(TreeRule, structure.Rule):
    """
    This rule checks that a sequential always block assigns a signal once in a sequence of statements, not first a
    default and then again in a later statement, as the STARC guide asks (2.2.3.3); in a combinational block it
    checks nonblocking assignments the same way (2.2.3.2). The signals are compared by their whole target, so q[0]
    and q[1] are different. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i) begin
           q <= 1'b0;
           if (load) q <= d;
       end

    **Fix**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i)
           if (load) q <= d;
           else q <= 1'b0;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oBlock in oFile.nodes("AlwaysBlock", "AlwaysFFBlock", "AlwaysCombBlock", "AlwaysLatchBlock"):
            lClocks, _ = clock_events(oBlock) if oBlock.kind.name in ("AlwaysBlock", "AlwaysFFBlock") else ([], [])
            lKinds = ASSIGNMENTS if lClocks or oBlock.kind.name == "AlwaysFFBlock" else ("NonblockingAssignmentExpression",)
            for oSequence in [o for o in descendants(oBlock) if o.kind.name == "SequentialBlockStatement"]:
                setSeen = set()
                for oItem in oSequence.items:
                    if not hasattr(oItem, "kind") or not oItem.kind.name.endswith("Statement"):
                        continue
                    dTargets = targets(oItem, lKinds)
                    for sTarget, oFirst in dTargets.items():
                        if sTarget in setSeen:
                            oToken = oFile.token_at(oFirst)
                            if oToken is not None:
                                yield Problem(oToken, f"Assign {sTarget} once: it is already assigned before in the block")
                    setSeen.update(dTargets)


def targets(oStatement, lKinds):
    """{target text: first token} of the assignments of the given kinds under a statement, in order."""
    dReturn = {}
    for oNode in [oStatement, *descendants(oStatement)]:
        if oNode.kind.name in lKinds and oNode.left is not None and not inside_for_header(oNode):
            dReturn.setdefault("".join(source(oNode.left).split()), oNode.left.getFirstToken())
    return dReturn


def inside_for_header(oNode):
    """True for an assignment in the header of a for loop, such as i = i + 1."""
    return oNode.parent is not None and oNode.parent.kind.name == "ForLoopStatement"
