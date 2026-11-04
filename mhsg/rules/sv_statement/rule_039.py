# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules import sv_types
from mhsg.rules.sv_tree import TreeRule


class rule_039(TreeRule, structure.Rule):
    """
    This rule checks that the target of an addition or a multiplication is wide enough for its result: one bit more
    than the widest operand of an addition, the sum of the widths for a multiplication, as the STARC guide asks
    (2.10.6.1). An operation with a constant, such as count + 1, is not checked. The widths come from slang's
    elaboration of the file. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       assign sum = a + b;  // all 8 bits

    **Fix**

    .. code-block:: systemverilog

       assign sum = a + b;  // sum 9 bits
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        lFound = []
        for oNode in sv_types.nodes(oFile, "Assignment"):
            oRight = sv_types.own(oNode.right)
            if oRight is None or oRight.kind.name != "BinaryOp" or sv_types.operator(oRight) not in ("Add", "Multiply"):
                continue
            if sv_types.constant(oRight.left) or sv_types.constant(oRight.right):
                continue
            iA, iB, iTarget = sv_types.width(oRight.left), sv_types.width(oRight.right), sv_types.width(oNode.left)
            if None in (iA, iB, iTarget):
                continue
            iWanted = max(iA, iB) + 1 if sv_types.operator(oRight) == "Add" else iA + iB
            if iTarget < iWanted:
                lFound.append((oNode, f"Make {sv_types.text(oNode.left)} {iWanted} bits wide to hold the result of {sv_types.text(oRight)}"))
        return sv_types.problems(oFile, lFound)
