# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_005(TreeRule, structure.Rule):
    """
    This rule checks for tasks in design code, as the STARC guide asks (2.1.2.4): use functions. It is disabled
    by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       task automatic load(input int value);

    **Fix**

    .. code-block:: systemverilog

       function automatic int load(input int value);
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("TaskDeclaration"):
            oToken = oFile.token_at(oNode.getFirstToken())
            if oToken is not None:
                yield Problem(oToken, "Use a function instead of a task")
