# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_025(TreeRule, structure.Rule):
    """
    This rule checks for $fdisplay, as the STARC guide recommends (4.1.11.1): write result files with $fstrobe, which
    writes the values at the end of the time step. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       $fdisplay(log, "%h", data);

    **Fix**

    .. code-block:: systemverilog

       $fstrobe(log, "%h", data);
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("InvocationExpression"):
            if (
                oNode.left is not None
                and oNode.left.kind.name == "SystemName"
                and text(oNode.left.systemIdentifier) in ("$fdisplay", "$fdisplayb", "$fdisplayh", "$fdisplayo")
            ):
                oToken = oFile.token_at(oNode.left.systemIdentifier)
                if oToken is not None:
                    yield Problem(oToken, f"Use $fstrobe instead of {text(oNode.left.systemIdentifier)}")
