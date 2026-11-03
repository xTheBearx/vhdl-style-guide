# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule, descendants


class rule_005(TreeRule, structure.Rule):
    """
    This rule checks that an always block has a single event control, at its start, as the STARC guide asks
    (2.2.2.3). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       always @(posedge clk_i) begin
           @(posedge clk_i) q <= d;

    **Fix**

    .. code-block:: systemverilog

       always @(posedge clk_i) begin
           q <= d;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oBlock in oFile.nodes("AlwaysBlock", "AlwaysFFBlock", "AlwaysCombBlock", "AlwaysLatchBlock"):
            oStatement = oBlock.statement
            if oStatement is not None and oStatement.kind.name == "TimingControlStatement":
                oStatement = oStatement.statement
            if oStatement is None:
                continue
            for oNode in descendants(oStatement):
                if oNode.kind.name == "TimingControlStatement":
                    oToken = oFile.token_at(oNode.getFirstToken())
                    if oToken is not None:
                        yield Problem(oToken, "Use a single event control, at the start of the always block")
