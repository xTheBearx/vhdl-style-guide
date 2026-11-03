# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_002(TreeRule, structure.Rule):
    """
    This rule checks that the default item of a case statement is its last item.

    |unfixable|

    **Violation**

    .. code-block:: systemverilog

       case (state_q)
           default: state_d = Idle;
           Idle:    state_d = Busy;
       endcase

    **Fix**

    .. code-block:: systemverilog

       case (state_q)
           Idle:    state_d = Busy;
           default: state_d = Idle;
       endcase
    """

    def __init__(self):
        super().__init__()
        self.solution = "Move the default item to the end of the case statement"

    def problems(self, oFile):
        for oCase in oFile.nodes("CaseStatement"):
            lItems = list(oCase.items)
            for oItem in lItems[:-1]:
                if oItem.kind.name == "DefaultCaseItem":
                    oToken = oFile.token_at(oItem.getFirstToken())
                    if oToken is not None:
                        yield Problem(oToken, self.solution)
