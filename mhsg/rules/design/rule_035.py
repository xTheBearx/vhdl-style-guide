# -*- coding: utf-8 -*-

from mhsg.design import cdc, control
from mhsg.design.rule import Finding, Rule


class rule_035(Rule):
    """
    This rule reports designs with registers in more than one clock domain, and clocks whose registers take both edges.

    .. NOTE:: This is a design rule. It runs in design analysis. It is disabled by default: many designs need more
              than one clock.

    One clock and one active edge keep timing analysis and test simple: no clock domain crossings, no half-cycle
    paths. Related clocks, such as the outputs of one PLL or a divided clock, are one domain. A register clocked
    through an inverter takes the other edge.

    **Violation**

    Registers clocked by clk_a and by clk_b, or on rising_edge(clk) and on falling_edge(clk).
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.disabled_in_design = True
        self.solution = "Use one clock and one edge, where the design allows it"

    def check_design(self, oContext):
        oAnalysis = oContext.cdc()
        if oAnalysis is None:
            return []
        oFlat = oAnalysis.flat
        dGroups = {}
        for oCell in oFlat.cells:
            oDomain = oAnalysis.cell_clock.get(id(oCell))
            if oDomain is None or not cdc.is_register(oCell):
                continue
            dGroup = dGroups.setdefault(oDomain.group, {"domains": [], 0: [], 1: []})
            if oDomain not in dGroup["domains"]:
                dGroup["domains"].append(oDomain)
            dGroup[control.clock_polarity(oAnalysis, oCell)].append(oCell)
        lReturn = []
        for dGroup in dGroups.values():
            for iEdge in (0, 1):
                dGroup[iEdge].sort(key=oFlat.cell_name)
        lGroups = sorted(dGroups.values(), key=lambda d: self.domain_name(d).lower())
        if len(lGroups) > 1:
            oFirst = (lGroups[1][1] or lGroups[1][0])[0]
            sFile, iLine = control.locate(oContext, oFlat, oFirst)
            sNames = ", ".join(self.domain_name(d) for d in lGroups)
            lReturn.append(Finding(sFile, iLine, f"The design has registers in {len(lGroups)} clock domains: {sNames}"))
        for dGroup in lGroups:
            if not dGroup[0] or not dGroup[1]:
                continue
            iFewer = 0 if len(dGroup[0]) <= len(dGroup[1]) else 1
            sFile, iLine = control.locate(oContext, oFlat, dGroup[iFewer][0])
            sMessage = f"Clock {self.domain_name(dGroup)} clocks {len(dGroup[1])} registers on the rising edge and {len(dGroup[0])} on the falling edge"
            lReturn.append(Finding(sFile, iLine, sMessage))
        return lReturn

    @staticmethod
    def domain_name(dGroup):
        """The name of a clock domain: its clock from a port or a black box, else the first clock found."""
        lDomains = dGroup["domains"]
        return next((o.name for o in lDomains if o.kind in ("port", "box")), lDomains[0].name)
