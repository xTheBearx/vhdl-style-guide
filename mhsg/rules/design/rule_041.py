# -*- coding: utf-8 -*-

from mhsg.design import netlist
from mhsg.design.rule import Finding, Rule


class rule_041(Rule):
    """
    This rule reports latches that, in test mode, are neither held transparent nor enabled by the inverted clock.

    .. NOTE:: This is a design rule. It runs in design analysis. It is disabled by default: it needs the inputs that
              select test mode, see :code:`test_mode` in :doc:`design_analysis`.

    Scan test shifts through registers, not latches. A latch held open in test mode is a wire the test sees through; a
    single latch enabled while the clock of the registers is low, by the inverted clock, holds its data for the half
    cycle the registers need. Any other latch blocks the test. The enable is followed back as the clocks of
    design_039.

    **Violation**

    A latch enabled by a register output, with no test-mode forcing of the enable.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.disabled_in_design = True
        self.solution = "Force the latch open in test mode, or enable it by the inverted clock"

    def check_design(self, oContext):
        oTest = oContext.test_mode()
        if oTest is None:
            return []
        # The bits of a latch, such as those of a memory of latches, are reported together
        dFound = {}
        for oCell, sPin, iLevel in oTest.clocked_cells():
            if oCell.type not in netlist.LATCH_TYPES:
                continue
            oEnable = oCell.connections[sPin][0]
            iValue = oTest.value(oEnable)
            if iValue == iLevel:
                continue
            oSource = oTest.clock_source(oEnable)
            if iValue is None and oSource.problem is None and iLevel ^ oSource.inverted == 0:
                continue
            if iValue is not None:
                sProblem = "is held closed in test mode"
            elif oSource.problem is None:
                sProblem = f"is open while clock {oSource.name} is high, not transparent in test mode"
            else:
                sProblem = "is neither transparent in test mode nor enabled by the inverted clock"
            dFound.setdefault((oTest.flat.cell_name(oCell), sProblem), []).append(oCell)
        lReturn = []
        for (sName, sProblem), lCells in sorted(dFound.items()):
            lCells.sort(key=oTest.register_name)
            if len(lCells) == 1:
                sName = oTest.register_name(lCells[0])
            sBits = f" ({len(lCells)} bits)" if len(lCells) > 1 else ""
            sFile, iLine = oContext.locate_cell(lCells[0], sName.split(".")[-1].split("(")[0])
            lReturn.append(Finding(sFile, iLine, f"Latch {sName}{sBits} {sProblem}"))
        return lReturn
