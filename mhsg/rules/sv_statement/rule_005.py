# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_005(TreeRule, structure.Rule):
    """
    This rule checks for fork-join blocks in design code, as the STARC guide asks (2.7.4.3). It is disabled by
    default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       fork
           a = 1;
       join

    **Fix**

    .. code-block:: systemverilog

       begin
           a = 1;
       end
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("ParallelBlockStatement"):
            oToken = oFile.token_at(oNode.getFirstToken())
            if oToken is not None:
                yield Problem(oToken, "Use begin-end instead of fork-join")
