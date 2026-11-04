# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_016(TreeRule, structure.Rule):
    """
    This rule checks for delays in continuous assignments and net declarations, as the STARC guide recommends
    (2.3.1.4): give delays only in always blocks. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       assign #1 y = a;

    **Fix**

    .. code-block:: systemverilog

       assign y = a;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("ContinuousAssign", "NetDeclaration"):
            oDelay = getattr(oNode, "delay", None)
            if oDelay is not None and text(oDelay.getFirstToken()):
                oToken = oFile.token_at(oDelay.getFirstToken())
                if oToken is not None:
                    yield Problem(oToken, "Give delays only in always blocks")
