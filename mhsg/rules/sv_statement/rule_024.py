# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import inside
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_024(TreeRule, structure.Rule):
    """
    This rule checks for nonblocking assignments in initial blocks, as the STARC guide recommends (4.1.2.2): drive
    test stimulus with blocking assignments. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       initial start <= 1'b1;

    **Fix**

    .. code-block:: systemverilog

       initial start = 1'b1;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("NonblockingAssignmentExpression"):
            if inside(oNode, "InitialBlock"):
                oToken = oFile.token_at(oNode.operatorToken)
                if oToken is not None:
                    yield Problem(oToken, "Use a blocking assignment (=) in the initial block")
