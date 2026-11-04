# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules import sv_types
from mhsg.rules.sv_tree import TreeRule


class rule_042(TreeRule, structure.Rule):
    """
    This rule checks for reduction operators, such as &data, whose 1-bit result is extended to a wider context, such
    as an addition or a wider target, as the STARC guide recommends (2.1.4.6). The widths come from slang's
    elaboration of the file. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       assign count = &a + &b;

    **Fix**

    .. code-block:: systemverilog

       assign count = {1'b0, &a} + {1'b0, &b};
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        lFound = []
        for oNode in sv_types.nodes(oFile, "Conversion"):
            oOperand = oNode.operand
            if (
                oOperand.kind.name != "UnaryOp"
                or not sv_types.operator(oOperand).startswith(("Bitwise", "Reduction"))
                or sv_types.operator(oOperand) == "BitwiseNot"
            ):
                continue
            iWidth = getattr(oNode.type, "bitWidth", None)
            if iWidth is not None and iWidth > 1:
                lFound.append((oOperand, f"The reduction {sv_types.text(oOperand)} gives 1 bit, here extended to {iWidth}"))
        return sv_types.problems(oFile, lFound)
