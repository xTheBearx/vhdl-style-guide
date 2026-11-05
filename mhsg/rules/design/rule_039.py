# -*- coding: utf-8 -*-

from mhsg.design import netlist, test_mode as tm
from mhsg.design.rule import Finding, Rule

TEXT = {
    tm.FROM_REGISTER: "comes from register {detail}, not from a top-level input",
    tm.FROM_LATCH: "comes from latch {detail}, not from a top-level input",
    tm.FROM_BOX: "comes from black box output {detail}, not declared as a clock output",
    tm.GATED: "passes a gate whose other input, {detail}, is not held in test mode",
    tm.MULTIPLEXER: "passes a clock multiplexer whose select, {detail}, is not held in test mode",
    tm.CONSTANT: "is held at {detail}",
    tm.UNKNOWN: "cannot be followed to a top-level input",
}


class rule_039(Rule):
    """
    This rule reports registers whose clock the tester does not control in test mode: the clock does not come from a
    top-level input, or the clock output of a black box such as a PLL, through buffers, inverters, and gates and
    multiplexers whose other inputs are held in test mode.

    .. NOTE:: This is a design rule. It runs in design analysis. It is disabled by default: it needs the inputs that
              select test mode, see :code:`test_mode` in :doc:`design_analysis`.

    In scan test, every register shifts and captures on a clock the tester drives. A clock made by a register, such as
    a divider, or by a latch, needs a multiplexer that selects a top-level clock in test mode; a gated clock needs its
    gating signal forced, with an OR into an AND gate or an AND into an OR gate, so the clock passes; a multiplexer of
    clocks needs its select fixed. The values of the test_mode inputs of the design section are propagated through
    the logic to decide which gates and multiplexers pass the clock.

    **Violation**

    A clock divider whose output clocks registers, with no test-mode multiplexer.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.disabled_in_design = True
        self.solution = "Select a top-level clock in test mode, or force the gating signal so the clock passes"

    def check_design(self, oContext):
        oTest = oContext.test_mode()
        if oTest is None:
            return []
        oFlat = oTest.flat
        dProblems = {}
        for oCell, sPin, _ in oTest.clocked_cells():
            if oCell.type in netlist.LATCH_TYPES:
                continue
            oSource = oTest.clock_source(oCell.connections[sPin][0])
            if oSource.problem is None:
                continue
            tKey = (oSource.problem, oSource.detail, id(oSource.cell) if oSource.cell is not None else None)
            dProblems.setdefault(tKey, (oSource, []))[1].append(oCell)
        lReturn = []
        for oSource, lCells in dProblems.values():
            lCells.sort(key=oTest.register_name)
            sCells = oTest.register_name(lCells[0]) + (f" and {len(lCells) - 1} more" if len(lCells) > 1 else "")
            oWhere = oSource.cell if oSource.cell is not None else lCells[0]
            sFile, iLine = oContext.locate_cell(oWhere, oFlat.cell_name(oWhere).split(".")[-1])
            sText = TEXT[oSource.problem].format(detail=oSource.detail)
            lReturn.append(Finding(sFile, iLine, f"In test mode, the clock of {sCells} {sText}"))
        return sorted(lReturn, key=lambda o: (o.file or "", o.line, o.message))
