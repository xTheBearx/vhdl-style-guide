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
        lReturn = []
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
            sName = oTest.register_name(oCell)
            sFile, iLine = oContext.locate_cell(oCell, sName.split(".")[-1])
            if iValue is not None:
                sMessage = f"Latch {sName} is held closed in test mode"
            elif oSource.problem is None:
                sMessage = f"Latch {sName} is open while clock {oSource.name} is high, not transparent in test mode"
            else:
                sMessage = f"Latch {sName} is neither transparent in test mode nor enabled by the inverted clock"
            lReturn.append(Finding(sFile, iLine, sMessage))
        return lReturn
