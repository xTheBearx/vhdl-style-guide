# -*- coding: utf-8 -*-

from mhsg.design import netlist
from mhsg.design.rule import Finding, Rule


class rule_040(Rule):
    """
    This rule reports clocks that, in test mode, reach registers on both edges.

    .. NOTE:: This is a design rule. It runs in design analysis. It is disabled by default: it needs the inputs that
              select test mode, see :code:`test_mode` in :doc:`design_analysis`.

    In scan test, the registers of a scan chain shift on one edge of one clock. Registers on the other edge of the same
    clock, such as those of a falling_edge process or behind an inverter, need a test-mode multiplexer that brings
    their clock to the phase of the others. The clocks are followed back as in design_039; registers whose clock is not
    controlled in test mode are left to it.

    **Violation**

    Registers on rising_edge(clk) and on falling_edge(clk), with no test-mode selection of the inverted clock.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.disabled_in_design = True
        self.solution = "In test mode, select the clock so all registers take the same edge"

    def check_design(self, oContext):
        oTest = oContext.test_mode()
        if oTest is None:
            return []
        oFlat = oTest.flat
        dSources = {}
        for oCell, sPin, iLevel in oTest.clocked_cells():
            if oCell.type in netlist.LATCH_TYPES:
                continue
            oSource = oTest.clock_source(oCell.connections[sPin][0])
            if oSource.problem is not None:
                continue
            dSources.setdefault(oSource.name, {0: [], 1: []})[iLevel ^ oSource.inverted].append(oCell)
        lReturn = []
        for sSource, dEdges in sorted(dSources.items()):
            if not dEdges[0] or not dEdges[1]:
                continue
            iFewer = 0 if len(dEdges[0]) <= len(dEdges[1]) else 1
            oFirst = sorted(dEdges[iFewer], key=oTest.register_name)[0]
            sFile, iLine = oContext.locate_cell(oFirst, oFlat.cell_name(oFirst).split(".")[-1])
            sMessage = f"In test mode, clock {sSource} reaches {len(dEdges[1])} registers on the rising edge and {len(dEdges[0])} on the falling edge"
            lReturn.append(Finding(sFile, iLine, sMessage))
        return lReturn
