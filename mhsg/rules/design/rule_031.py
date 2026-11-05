# -*- coding: utf-8 -*-

from mhsg.design.rule import Finding, Rule


class rule_031(Rule):
    """
    This rule reports instances whose own registers are in more than one clock domain.

    .. NOTE:: This is a design rule. It runs in design analysis. It is disabled by default: a design need not follow
              it, and synchronizers and clock domain crossing blocks have two domains by design.

    A block in one clock domain is constrained, synthesized and verified on its own, and its crossings are at its
    ports. The registers of the instance itself are counted, not those of the instances in it. Related clocks, such as
    the outputs of one PLL, are one domain.

    **Violation**

    An entity with processes on two unrelated clocks.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.disabled_in_design = True
        self.solution = "Give each clock domain a block of its own"

    def check_design(self, oContext):
        oAnalysis = oContext.cdc()
        if oAnalysis is None:
            return []
        oFlat = oAnalysis.flat
        dInstances = {}
        for oCell in oFlat.cells:
            oDomain = oAnalysis.cell_clock.get(id(oCell))
            if oDomain is None:
                continue
            dGroups = dInstances.setdefault(oCell.path, {})
            dGroups.setdefault(oDomain.group, (oDomain, oCell))
        lReturn = []
        for tPath, dGroups in sorted(dInstances.items()):
            if len(dGroups) < 2:
                continue
            lDomains = sorted(o.name for o, _ in dGroups.values())
            oFirst = next(iter(dGroups.values()))[1]
            sFile, iLine = oContext.locate_cell(oFirst)
            sWhere = "instance " + ".".join(tPath) if tPath else "the top-level module"
            lReturn.append(Finding(sFile, iLine, f"Registers of {sWhere} are in {len(dGroups)} clock domains: {', '.join(lDomains)}"))
        return lReturn
