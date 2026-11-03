# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule, descendants


class rule_002(TreeRule, structure.Rule):
    """
    This rule checks that always_comb blocks use blocking assignments (=), not nonblocking ones (<=).

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
        for oBlock in oFile.nodes("AlwaysCombBlock"):
            for oNode in descendants(oBlock):
                if oNode.kind.name == "NonblockingAssignmentExpression":
                    oToken = oFile.token_at(oNode.operatorToken)
                    if oToken is not None:
                        yield Problem(oToken, self.solution)

    def _fix_violation(self, oViolation):
        oViolation.get_tokens()[0].set_value("=")
