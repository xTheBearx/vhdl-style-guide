# -*- coding: utf-8 -*-

import functools

from mhsg.design import control, graph
from mhsg.design.rule import Finding, Rule

# The roles of black box outputs made to drive each kind of control pin
ALLOWED = {control.CLOCK: ("clock_out",), control.RESET: ("reset_out",), control.TRISTATE: ()}


class rule_032(Rule):
    """
    This rule reports black box outputs that drive a clock, an asynchronous reset or a tri-state enable, directly or
    through logic.

    .. NOTE:: This is a design rule. It runs in design analysis.

    The logic of a black box is not seen by design analysis, nor controlled by scan test, so a clock, reset or enable
    it makes is neither checked nor testable. Outputs declared as clocks or resets of the box, see
    the black boxes of :doc:`design_analysis`, such as those of a clock buffer, a PLL or a reset controller, are made for it
    and not reported, nor is the reset of a reset synchronizer, which makes a reset from any signal, such as the lock
    output of a PLL. A path through a box, such as an input buffer, is followed to what drives it.

    **Violation**

    The ready output of a vendor IP used as the clock of a register.
    """

    def __init__(self):
        super().__init__()
        self.solution = "Make clocks, resets and tri-state enables in the design, or declare the output as a clock or reset of the box"

    def check_design(self, oContext):
        oAnalysis = oContext.cdc()
        if oAnalysis is None:
            return []
        oFlat = oAnalysis.flat
        dFound = {}
        dMemo = {}
        for oCell, sPort, sKind in control.control_pins(oFlat):
            # A reset synchronizer takes its reset from anywhere, such as the lock output of a PLL: it makes the reset
            if sKind == control.RESET and oAnalysis.is_reset_synchronizer(oCell, dMemo):
                continue
            for oNet in oCell.connections.get(sPort, []):
                if not graph.is_variable(oNet):
                    continue
                for tPoint in oAnalysis.sources(oNet):
                    oBox, sOutput, _ = tPoint
                    if oBox is None or not oBox.is_black_box():
                        continue
                    oRole = oAnalysis.box_role(oBox, sOutput)
                    if oRole is not None and oRole.kind in ALLOWED[sKind]:
                        continue
                    lCells = dFound.setdefault((oAnalysis.point_name(tPoint), sKind), [])
                    if oCell not in lCells:
                        lCells.append(oCell)
        lReturn = []
        for (sOutput, sKind), lCells in sorted(dFound.items(), key=lambda t: t[0]):
            sPort = "Y" if sKind == control.TRISTATE else "Q"
            lCells = sorted(lCells, key=functools.partial(oFlat.cell_name, sPort=sPort))
            sFile, iLine = control.locate(oContext, oFlat, lCells[0], sPort)
            sMore = f" and {len(lCells) - 1} more" if len(lCells) > 1 else ""
            sTarget = oFlat.cell_name(lCells[0], sPort)
            lReturn.append(Finding(sFile, iLine, f"Black box output {sOutput} drives the {sKind} of {sTarget}{sMore}"))
        return lReturn
