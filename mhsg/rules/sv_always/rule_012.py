# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_always.rule_007 import reset_names
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants


class rule_012(TreeRule, structure.Rule):
    """
    This rule checks that an edge triggered always block has one clock, on one edge, as the STARC guide asks
    (2.3.3.1, 2.3.3.2). The events its first if tests are asynchronous resets, not clocks. It is disabled by default;
    the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       always_ff @(posedge clk_a or posedge clk_b) begin
           q <= d;
       end

    **Fix**

    Split the always block into one for each clock.

    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oBlock in oFile.nodes("AlwaysBlock", "AlwaysFFBlock"):
            lClocks, _ = clock_events(oBlock)
            if len(lClocks) > 1:
                oToken = oFile.token_at(lClocks[1].edge)
                if oToken is not None:
                    yield Problem(oToken, "Clock the always block on one edge of one clock")


def clock_events(oBlock):
    """(clock events, reset events) of an edge triggered always block: the events its first if tests are resets."""
    oStatement = oBlock.statement
    if oStatement is None or oStatement.kind.name != "TimingControlStatement":
        return [], []
    lEvents = [o for o in descendants(oStatement.timingControl) if o.kind.name == "SignalEventExpression" and text(o.edge)]
    setResets = reset_names(oStatement.statement) if len(lEvents) > 1 else set()
    lClocks = [o for o in lEvents if text(o.expr.getFirstToken()) not in setResets]
    lResets = [o for o in lEvents if text(o.expr.getFirstToken()) in setResets]
    return lClocks, lResets
