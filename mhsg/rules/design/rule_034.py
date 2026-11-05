# -*- coding: utf-8 -*-

from mhsg.design import control
from mhsg.design.rule import Finding, Rule


class rule_034(Rule):
    """
    This rule reports clocks and asynchronous resets made inside the design outside of a clock or reset generation
    block: in the top-level module itself, or in a block under the top level that also holds registers they clock or
    reset.

    .. NOTE:: This is a design rule. It runs in design analysis. It is disabled by default: a design need not follow
              it.

    Clocks made by a register, such as a divider, by logic, such as a gate or a multiplexer, or by a PLL, and resets
    made by a register or logic, such as a reset synchronizer, belong in blocks of their own, instantiated in the top
    level: their timing is then constrained in one place, and test logic, such as the test-mode selection of a clock,
    is added there without changing the blocks they drive. The block of a clock or reset is the instance under the top
    level that holds the cell making it.

    **Violation**

    A clock divider in the same block as the registers it clocks.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.disabled_in_design = True
        self.solution = "Move the generation of clocks and resets into blocks of their own, instantiated in the top level"

    def check_design(self, oContext):
        oAnalysis = oContext.cdc()
        if oAnalysis is None:
            return []
        oFlat = oAnalysis.flat
        dDomainCells = control.domain_cells(oAnalysis)
        lReturn = []
        for oDomain, oCell in control.generated_clocks(oAnalysis):
            sProblem = self.problem(oCell, dDomainCells.get(oDomain.key, []))
            if sProblem is not None:
                sFile, iLine = oContext.locate_cell(oCell, oDomain.name.split(".")[-1])
                lReturn.append(Finding(sFile, iLine, f"Clock {oDomain.name} is generated in {sProblem}"))
        for oRoot, oCell, lCells in control.generated_resets(oAnalysis):
            sProblem = self.problem(oCell, lCells)
            if sProblem is not None:
                sFile, iLine = control.locate(oContext, oFlat, oCell)
                sReset = oFlat.net_name(oRoot)
                if sReset.startswith("net "):
                    # A reset made by logic has no name of its own: name it after its inputs
                    sReset = "made by logic of " + ", ".join(sorted({oAnalysis.point_name(t) for t in oAnalysis.sources(oRoot)}))
                lReturn.append(Finding(sFile, iLine, f"Reset {sReset} is generated in {sProblem}"))
        return lReturn

    @staticmethod
    def problem(oCell, lDriven):
        """What is wrong with where a clock or reset is made, or None when it is in a block of its own."""
        if not oCell.path:
            return "the top-level module, not in a block of its own"
        tBlock = oCell.path[:1]
        if any(o.path[:1] == tBlock for o in lDriven):
            sInstance = "" if len(oCell.path) == 1 else f"instance {'.'.join(oCell.path)} of "
            return f"{sInstance}block {tBlock[0]}, which also holds registers it drives"
        return None
