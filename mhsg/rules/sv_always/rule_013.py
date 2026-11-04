# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_always.rule_012 import clock_events
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants, elements


class rule_013(TreeRule, structure.Rule):
    """
    This rule checks that an asynchronous reset is active low, tested on its falling edge with negedge, as the STARC
    guide recommends (2.3.6.2). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i or posedge rst_i) begin
           if (rst_i) q <= 1'b0;
           else q <= d;
       end

    **Fix**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i or negedge rst_ni) begin
           if (!rst_ni) q <= 1'b0;
           else q <= d;
       end
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oBlock in oFile.nodes("AlwaysBlock", "AlwaysFFBlock"):
            _, lResets = clock_events(oBlock)
            for oReset in lResets:
                if text(oReset.edge) == "posedge":
                    oToken = oFile.token_at(oReset.edge)
                    if oToken is not None:
                        yield Problem(oToken, "Make the asynchronous reset active low, with negedge")
