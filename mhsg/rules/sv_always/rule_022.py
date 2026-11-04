# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.port.rule_028 import clock_reset_rank
from mhsg.rules.sv_always.rule_012 import clock_events
from mhsg.rules.sv_nodes import inside, text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants


class rule_022(TreeRule, structure.Rule):
    """
    This rule checks that clocks, the signals of the edge events of always blocks other than their asynchronous
    resets, are not read as data, in assignments or conditions, as the STARC guide asks (1.4.3.4, 3.3.3.1): a clock
    drives only the clock inputs of registers. Signals named as resets, as for port_028, are not taken for clocks. It
    is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i) q <= d;
       assign y = clk_i & en;

    **Fix**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i) q <= d;
       assign y = en;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        setClocks = set()
        setResets = set()
        for oBlock in oFile.nodes("AlwaysBlock", "AlwaysFFBlock"):
            lClocks, lResets = clock_events(oBlock)
            setClocks.update(text(o.expr.getFirstToken()) for o in lClocks)
            setResets.update(text(o.expr.getFirstToken()) for o in lResets)
        # A reset is taken for a clock in a block that does not test it first; its name tells it apart too
        setClocks = {s for s in setClocks if s not in setResets and clock_reset_rank(s) != 1}
        if not setClocks:
            return
        # The clock an assignment toggles, as in clk = ~clk, is not read as data
        lRead = [(o.right, text(o.left.getFirstToken())) for o in oFile.nodes("NonblockingAssignmentExpression", "AssignmentExpression") if o.right is not None]
        lRead += [(o, None) for o in oFile.nodes("ConditionalPredicate")]
        lRead += [(o.expr, None) for o in oFile.nodes("CaseStatement") if o.expr is not None]
        for oRead, sAssigned in lRead:
            for oName in [oRead, *descendants(oRead)]:
                sName = text(oName.identifier) if oName.kind.name in ("IdentifierName", "IdentifierSelectName") else None
                if sName in setClocks and sName != sAssigned and not inside(oName, "EventControlWithExpression"):
                    oToken = oFile.token_at(oName.identifier)
                    if oToken is not None:
                        yield Problem(oToken, f"Do not use the clock {text(oName.identifier)} as data")
