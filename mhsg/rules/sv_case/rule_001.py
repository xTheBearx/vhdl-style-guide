# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule
from mhsg.vhdlFile import utils


class rule_001(TreeRule, structure.Rule):
    """
    This rule checks that a case statement has a default item, unless it is unique or unique0 and
    **exempt_unique** is yes, the default.

    |unfixable|

    **Violation**

    .. code-block:: systemverilog

       case (state_q)
           Idle: state_d = Busy;
           Busy: state_d = Idle;
       endcase

    **Fix**

    .. code-block:: systemverilog

       case (state_q)
           Idle:    state_d = Busy;
           Busy:    state_d = Idle;
           default: state_d = Idle;
       endcase
    """

    def __init__(self):
        super().__init__()
        self.solution = "Add a default item"
        self.exempt_unique = "yes"
        self.configuration.append("exempt_unique")

    def problems(self, oFile):
        bExemptUnique = utils.convert_yes_no_option_to_boolean(self.exempt_unique)
        for oCase in oFile.nodes("CaseStatement"):
            if bExemptUnique and oCase.uniqueOrPriority is not None and oCase.uniqueOrPriority.rawText in ("unique", "unique0"):
                continue
            if any(o.kind.name == "DefaultCaseItem" for o in oCase.items):
                continue
            oToken = oFile.token_at(oCase.caseKeyword)
            if oToken is not None:
                yield Problem(oToken, self.solution)
