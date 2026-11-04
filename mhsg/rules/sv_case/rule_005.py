# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants, elements


class rule_005(TreeRule, structure.Rule):
    """
    This rule checks for casex and casez statements, as the STARC guide recommends (2.8.4.3). It is disabled by
    default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       casez (sel)
           2'b1?: y = a;
           default: y = b;
       endcase

    **Fix**

    .. code-block:: systemverilog

       case (sel[1])
           1'b1: y = a;
           default: y = b;
       endcase
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oCase in oFile.nodes("CaseStatement"):
            if text(oCase.caseKeyword) in ("casex", "casez"):
                oToken = oFile.token_at(oCase.caseKeyword)
                if oToken is not None:
                    yield Problem(oToken, f"Use case instead of {text(oCase.caseKeyword)}")
