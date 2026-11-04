# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_case.rule_008 import state_cases
from mhsg.rules.sv_nodes import source
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_010(TreeRule, structure.Rule):
    """
    This rule checks that a module has at most one state machine, a case statement whose selector matches
    **state_pattern**, as the STARC guide recommends (2.11.2.1): put each state machine in a module of its own. It is
    disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       case (tx_state) ...
       case (rx_state) ...

    **Fix**

    Put each state machine in a module of its own.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"
        self.state_pattern = ".*state.*"
        self.configuration.append("state_pattern")

    def problems(self, oFile):
        for oModule in oFile.nodes("ModuleDeclaration"):
            iStart, iEnd = oModule.getFirstToken().location.offset, oModule.getLastToken().location.offset
            dFirst = {}
            for oCase in state_cases(oFile, self.state_pattern):
                if not iStart <= oCase.getFirstToken().location.offset <= iEnd:
                    continue
                sName = source(oCase.expr).strip("()")
                if sName not in dFirst and dFirst:
                    oToken = oFile.token_at(oCase.caseKeyword)
                    if oToken is not None:
                        yield Problem(oToken, f"Put the state machine of {sName} in a module of its own")
                dFirst.setdefault(sName, oCase)
