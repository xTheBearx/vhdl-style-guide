# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules import sv_types
from mhsg.rules.sv_tree import TreeRule


class rule_040(TreeRule, structure.Rule):
    """
    This rule checks the operands of divisions and remainders: the dividend at most **maximum_dividend_bits** wide,
    12 by default, and the divisor at most **maximum_divisor_bits**, 8 by default, unless it is a constant power of
    two, as the STARC guide asks (2.10.8.2, 2.10.8.3). The widths come from slang's elaboration of the file. It is
    disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       assign q = a / b;  // 16 and 16 bits

    **Fix**

    Use a divider built for the widths, or narrower operands.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"
        self.maximum_dividend_bits = 12
        self.configuration.append("maximum_dividend_bits")
        self.maximum_divisor_bits = 8
        self.configuration.append("maximum_divisor_bits")

    def problems(self, oFile):
        lFound = []
        for oNode in sv_types.nodes(oFile, "BinaryOp"):
            if sv_types.operator(oNode) not in ("Divide", "Mod"):
                continue
            iDividend, iDivisor = sv_types.width(oNode.left), sv_types.width(oNode.right)
            if sv_types.value(oNode.left) is None and iDividend is not None and iDividend > int(self.maximum_dividend_bits):
                lFound.append((oNode, f"Divide at most {self.maximum_dividend_bits} bits: {sv_types.text(oNode.left)} has {iDividend}"))
            iValue = sv_types.value(oNode.right)
            if iValue is not None and iValue > 0 and iValue & (iValue - 1) == 0:
                continue
            if iValue is None and iDivisor is not None and iDivisor > int(self.maximum_divisor_bits):
                lFound.append((oNode, f"Divide by at most {self.maximum_divisor_bits} bits: {sv_types.text(oNode.right)} has {iDivisor}"))
        return sv_types.problems(oFile, lFound)
