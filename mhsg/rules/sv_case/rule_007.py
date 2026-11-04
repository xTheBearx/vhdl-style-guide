# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_007(TreeRule, structure.Rule):
    """
    This rule checks that the selector of a case statement is a signal, a select or a concatenation, not logic or
    arithmetic, as the STARC guide recommends (2.8.5.4). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       case (a & b)
           1'b1: y = c;
           default: y = d;
       endcase

    **Fix**

    .. code-block:: systemverilog

       assign both = a & b;
       ...
       case (both)
           1'b1: y = c;
           default: y = d;
       endcase
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oCase in oFile.nodes("CaseStatement"):
            oSelector = oCase.expr
            while oSelector is not None and oSelector.kind.name == "ParenthesizedExpression":
                oSelector = oSelector.expression
            if oSelector is not None and hasattr(oSelector, "operatorToken"):
                oToken = oFile.token_at(oSelector.getFirstToken())
                if oToken is not None:
                    yield Problem(oToken, "Compute the case selector in a signal of its own")
