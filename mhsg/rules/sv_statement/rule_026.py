# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_026(TreeRule, structure.Rule):
    """
    This rule checks for the logical operators &&, || and !, as the STARC guide recommends (2.1.4.2): use the bitwise
    operators &, | and ~, also on single bits. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       if (valid && !stall) q <= d;

    **Fix**

    .. code-block:: systemverilog

       if (valid & ~stall) q <= d;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("LogicalAndExpression", "LogicalOrExpression", "UnaryLogicalNotExpression"):
            oToken = oFile.token_at(oNode.operatorToken)
            if oToken is not None:
                yield Problem(oToken, f"Use the bitwise operator instead of {text(oNode.operatorToken)}")
