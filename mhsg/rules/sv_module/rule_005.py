# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_005(TreeRule, structure.Rule):
    """
    This rule checks for gate primitives, such as and or nand instances, which can build latches and flip-flops out
    of gates, as the STARC guide asks (1.2.1.2). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       nand g_set (q, set_n, qb);

    **Fix**

    .. code-block:: systemverilog

       assign q = ~(set_n & qb);
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("PrimitiveInstantiation"):
            oToken = oFile.token_at(oNode.type)
            if oToken is not None:
                yield Problem(oToken, f"Use an expression instead of the {text(oNode.type)} primitive")
