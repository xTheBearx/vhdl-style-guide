# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule, first_token, last_token
from mhsg.svFile import tokens


class rule_001(TreeRule, structure.Rule):
    """
    This rule checks that combinational logic uses always_comb rather than always @* or always @(*).

    **Violation**

    .. code-block:: systemverilog

       always @(*) begin
           sum = a + b;
       end

    **Fix**

    .. code-block:: systemverilog

       always_comb begin
           sum = a + b;
       end
    """

    def __init__(self):
        super().__init__()
        self.fixable = True
        self.solution = "Use always_comb"

    def problems(self, oFile):
        for oBlock in oFile.nodes("AlwaysBlock"):
            oStatement = oBlock.statement
            if oStatement is None or oStatement.kind.name != "TimingControlStatement":
                continue
            if oStatement.timingControl.kind.name != "ImplicitEventControl":
                continue
            oFirst = first_token(oFile, oBlock)
            oLast = last_token(oFile, oStatement.timingControl)
            if oFirst is not None and oLast is not None:
                yield Problem(oFirst, self.solution, oLast)

    def _fix_violation(self, oViolation):
        oViolation.set_tokens([tokens.keyword("always_comb", "AlwaysCombKeyword")])
