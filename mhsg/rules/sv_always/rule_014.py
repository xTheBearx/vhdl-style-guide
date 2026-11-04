# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_always.rule_012 import clock_events
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_014(TreeRule, structure.Rule):
    """
    This rule checks that a register has at most one asynchronous reset or set, as the STARC guide asks (1.3.1.7,
    2.3.1.7): an always block with more than one event besides its clock. It is disabled by default; the starc rule
    set enables it.

    **Violation**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i or negedge rst_ni or negedge set_ni) begin
       end

    **Fix**

    Keep one asynchronous reset, and set the register synchronously.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oBlock in oFile.nodes("AlwaysBlock", "AlwaysFFBlock"):
            lClocks, lResets = clock_events(oBlock)
            if len(lResets) > 1 or (len(lClocks) + len(lResets) > 2):
                oToken = oFile.token_at(oBlock.getFirstToken())
                if oToken is not None:
                    yield Problem(oToken, "Give the register at most one asynchronous reset or set")
