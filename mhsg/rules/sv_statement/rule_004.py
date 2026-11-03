# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_004(TreeRule, structure.Rule):
    """
    This rule checks for initial blocks in design code, which synthesis ignores, as the STARC guide asks
    (2.3.4.1, 2.3.4.2). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       initial count_q = '0;

    **Fix**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i or negedge rst_ni) begin
           if (!rst_ni) count_q <= '0;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("InitialBlock"):
            oToken = oFile.token_at(oNode.keyword)
            if oToken is not None:
                yield Problem(oToken, "Remove the initial block from design code")
