# -*- coding: utf-8 -*-

from mhsg.design.rule import Finding, Rule


class rule_012(Rule):
    """
    This rule reports gated clocks: clocks that pass through logic.

    .. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check SS10.

    Logic on a clock adds skew and can glitch, which clocks registers when they should not be.
    Use a clock enable instead, or a clock gating cell of the device.
    Registers on a gated clock are in the clock domain of the clock that is gated.

    **Violation**

    .. code-block:: vhdl

       clk_gated <= clk and enable;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Use a clock enable"

    def check_design(self, oContext):
        oAnalysis = oContext.cdc()
        if oAnalysis is None:
            return []
        lReturn = []
        for oDomain in sorted(oAnalysis.clocks.values(), key=lambda o: o.name):
            if oDomain.kind != "logic" or not oDomain.parent or oDomain.registers == 0:
                continue
            sFile, iLine = oAnalysis.locate(oDomain.cell, oDomain.name.split(".")[-1])
            lReturn.append(Finding(sFile, iLine, f"Clock {oDomain.parent.name} is gated by logic into {oDomain.name} ({registers(oDomain.registers)})"))
        return lReturn


def registers(iCount):
    return f"{iCount} register" if iCount == 1 else f"{iCount} registers"
