# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule, descendants

ARITHMETIC = ("AddExpression", "SubtractExpression", "MultiplyExpression", "DivideExpression", "ModExpression", "PowerExpression")


class rule_011(TreeRule, structure.Rule):
    """
    This rule checks for arithmetic in the condition of an if statement, as the STARC guide asks (2.10.7.1): compute
    it in a signal of its own. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       if (count + 1 == limit) begin
           done = 1'b1;
       end

    **Fix**

    .. code-block:: systemverilog

       assign next_count = count + 1;
       ...
       if (next_count == limit) begin
           done = 1'b1;
       end
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oIf in oFile.nodes("ConditionalStatement"):
            for oNode in descendants(oIf.predicate):
                if oNode.kind.name in ARITHMETIC:
                    oToken = oFile.token_at(oNode.operatorToken)
                    if oToken is not None:
                        yield Problem(oToken, "Compute the arithmetic outside the if condition")
                    break
