# -*- coding: utf-8 -*-

from mhsg.design import cdc
from mhsg.design.rule import Finding, Rule


class rule_038(Rule):
    """
    This rule reports data from a register of one clock domain that reaches a register of an unrelated clock domain
    without passing a latch.

    .. NOTE:: This is a design rule. It runs in design analysis. It is disabled by default: a synchronizer is enough
              for most designs.

    A latch enabled by the inverted source clock, between the source register and the register of the other domain,
    holds the data for the second half of the source clock period. It gives hold time to the transfer and, in scan
    test, where all registers shift on one clock, keeps the shift between the two scan chains from racing. Inputs of the
    top level, which have no source clock, are not reported; crossings without a synchronizer are also reported by
    design_008.

    **Violation**

    A register of clk_a feeding the first stage of a synchronizer clocked by clk_b.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.disabled_in_design = True
        self.solution = "Pass the data through a latch enabled by the inverted source clock"

    def check_design(self, oContext):
        oAnalysis = oContext.cdc()
        if oAnalysis is None:
            return []
        lReturn = []
        for oCrossing in oAnalysis.crossings:
            if not cdc.is_register(oCrossing.cell):
                continue
            dSources = {}
            for _, _, lPoints in getattr(oCrossing, "bits", []):
                for tPoint in lPoints:
                    oDomain = oAnalysis.domain_of(tPoint)
                    if cdc.is_register(tPoint[0]) and oDomain not in (None, "async"):
                        dSources.setdefault(oDomain.name, set()).add(oAnalysis.point_name(tPoint))
            if not dSources:
                continue
            sFile, iLine = oContext.locate_cell(oCrossing.cell, oCrossing.name.split(".")[-1])
            for sClock, setNames in sorted(dSources.items()):
                lNames = sorted(setNames)
                sNames = ", ".join(lNames[:3]) + (", ..." if len(lNames) > 3 else "")
                sMessage = f"{oCrossing.name} ({oCrossing.clock.name}) takes data from {sNames} ({sClock}) without a latch on the inverted {sClock}"
                lReturn.append(Finding(sFile, iLine, sMessage))
        return lReturn
