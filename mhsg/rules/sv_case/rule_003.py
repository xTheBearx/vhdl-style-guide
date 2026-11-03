# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_003(TreeRule, structure.Rule):
    """
    This rule checks for case statements whose selector is a constant, such as case (1'b1), as the STARC guide
    asks (2.8.5.2). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       case (1'b1)
           a: y = 0;

    **Fix**

    .. code-block:: systemverilog

       if (a) begin
           y = 0;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oCase in oFile.nodes("CaseStatement"):
            if oCase.expr is not None and oCase.expr.kind.name in ("IntegerVectorExpression", "IntegerLiteralExpression", "UnbasedUnsizedLiteralExpression"):
                oToken = oFile.token_at(oCase.caseKeyword)
                if oToken is not None:
                    yield Problem(oToken, "Use a signal as the case selector, not a constant")
