# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_always.rule_012 import clock_events
from mhsg.rules.sv_tree import Problem, TreeRule, descendants


class rule_026(TreeRule, structure.Rule):
    """
    This rule checks that the nonblocking assignments of edge triggered always blocks have a unit delay, such as q <=
    #1 d, as the STARC guide recommends (2.3.1.3) so that simulation shows the register change after the clock edge.
    It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i) q <= d;

    **Fix**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i) q <= #1 d;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oBlock in oFile.nodes("AlwaysBlock", "AlwaysFFBlock"):
            lClocks, _ = clock_events(oBlock)
            if not lClocks:
                continue
            for oNode in descendants(oBlock):
                if oNode.kind.name == "NonblockingAssignmentExpression" and oNode.right is not None and oNode.right.kind.name != "TimingControlExpression":
                    oToken = oFile.token_at(oNode.operatorToken)
                    if oToken is not None:
                        yield Problem(oToken, "Add a unit delay to the register assignment, as in <= #1")
