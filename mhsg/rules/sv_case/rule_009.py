# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_case.rule_008 import state_cases
from mhsg.rules.sv_tree import Problem, TreeRule, elements


class rule_009(TreeRule, structure.Rule):
    """
    This rule checks that a state machine, a case statement whose selector matches **state_pattern**, has at most
    **maximum_states** items, 60 by default, as the STARC guide asks (2.11.1.4, 2.11.1.5): split larger ones. It is
    disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       case (state)  // 75 states

    **Fix**

    Split the state machine into two that hand over to each other.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"
        self.state_pattern = ".*state.*"
        self.configuration.append("state_pattern")
        self.maximum_states = 60
        self.configuration.append("maximum_states")

    def problems(self, oFile):
        for oCase in state_cases(oFile, self.state_pattern):
            iStates = sum(len(list(elements(o.expressions))) for o in elements(oCase.items) if o.kind.name == "StandardCaseItem")
            if iStates > int(self.maximum_states):
                oToken = oFile.token_at(oCase.caseKeyword)
                if oToken is not None:
                    yield Problem(oToken, f"Split the state machine: it has {iStates} states, more than {self.maximum_states}")
