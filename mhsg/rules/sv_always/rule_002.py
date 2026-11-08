# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import combinational_blocks, is_verilog
from mhsg.rules.sv_tree import Problem, TreeRule, descendants


class rule_002(TreeRule, structure.Rule):
    """
    This rule checks that always_comb blocks use blocking assignments (=), not nonblocking ones (<=). In a Verilog
    file, which has no always_comb, it checks the always blocks of combinational logic: always @*, and those whose
    event control has no edge.

    **Violation**

    .. code-block:: systemverilog

       always_comb begin
           sum <= a + b;
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
        self.solution = "Use a blocking assignment (=) in always_comb"

    def problems(self, oFile):
        sSolution = "Use a blocking assignment (=) in combinational logic" if is_verilog(oFile) else self.solution
        for oBlock in combinational_blocks(oFile):
            for oNode in descendants(oBlock):
                if oNode.kind.name == "NonblockingAssignmentExpression":
                    oToken = oFile.token_at(oNode.operatorToken)
                    if oToken is not None:
                        yield Problem(oToken, sSolution)

    def _fix_violation(self, oViolation):
        oViolation.get_tokens()[0].set_value("=")
