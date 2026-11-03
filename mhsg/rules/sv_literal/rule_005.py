# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import has_x_or_z
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_005(TreeRule, structure.Rule):
    """
    This rule checks for comparisons with x or z, which are never true in synthesis, as the STARC guide asks
    (2.10.1.4). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       if (data == 8'bx) begin

    **Fix**

    .. code-block:: systemverilog

       if (data_valid) begin
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("EqualityExpression", "InequalityExpression", "CaseEqualityExpression", "CaseInequalityExpression"):
            if has_x_or_z(oNode.left) or has_x_or_z(oNode.right):
                oToken = oFile.token_at(oNode.operatorToken)
                if oToken is not None:
                    yield Problem(oToken, "Do not compare with x or z")
