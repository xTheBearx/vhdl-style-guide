# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules import sv_types
from mhsg.rules.sv_tree import TreeRule


class rule_041(TreeRule, structure.Rule):
    """
    This rule checks that the operands of multiplications of two signals are at most **maximum_multiplier_bits**
    wide, 16 by default, as the STARC guide recommends (2.10.6.5): build larger multipliers explicitly. The widths
    come from slang's elaboration of the file. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       assign p = a * b;  // 32 bits each

    **Fix**

    Build the multiplier from smaller ones, or use a multiplier core.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"
        self.maximum_multiplier_bits = 16
        self.configuration.append("maximum_multiplier_bits")

    def problems(self, oFile):
        lFound = []
        for oNode in sv_types.nodes(oFile, "BinaryOp"):
            if sv_types.operator(oNode) != "Multiply" or sv_types.value(oNode.left) is not None or sv_types.value(oNode.right) is not None:
                continue
            iWidest = max(sv_types.width(oNode.left) or 0, sv_types.width(oNode.right) or 0)
            if iWidest > int(self.maximum_multiplier_bits):
                lFound.append((oNode, f"Build the multiplier of {sv_types.text(oNode)} explicitly: its operands have up to {iWidest} bits"))
        return sv_types.problems(oFile, lFound)
