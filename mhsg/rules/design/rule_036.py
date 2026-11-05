# -*- coding: utf-8 -*-

from mhsg.design import control, graph
from mhsg.design.rule import Finding, Rule


class rule_036(Rule):
    """
    This rule reports registers and latches in the top-level module itself, other than those that make clocks and
    resets.

    .. NOTE:: This is a design rule. It runs in design analysis. It is disabled by default: a design need not follow
              it.

    The top level holds the blocks of the design, clock and reset generation, memories and I/O cells, and the
    connections between them. Logic with registers in the top level is timed and tested with the whole chip instead of
    in a block. Combinational glue logic is not reported, nor memories, nor the registers that make clocks and resets,
    such as dividers and reset synchronizers.

    **Violation**

    A process with a register in the architecture of the top-level entity.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.disabled_in_design = True
        self.solution = "Move the registers into a block"

    def check_design(self, oContext):
        oAnalysis = oContext.cdc()
        if oAnalysis is None:
            return []
        oFlat = oAnalysis.flat
        setMakers = {id(c) for _, c in control.generated_clocks(oAnalysis)} | {id(c) for _, c, _ in control.generated_resets(oAnalysis)}
        dMemo = {}
        lCells = []
        for oCell in oFlat.cells:
            if oCell.path or oCell.is_black_box() or oCell.type not in graph.STATE_TYPES or id(oCell) in setMakers:
                continue
            if oAnalysis.is_reset_synchronizer(oCell, dMemo):
                continue
            lCells.append(oCell)
        if not lCells:
            return []
        # Sorted by name, so the finding does not depend on the order of the cells in the netlist
        lCells.sort(key=oFlat.cell_name)
        lNames = sorted({oFlat.cell_name(o) for o in lCells})
        sNames = ", ".join(lNames[:4]) + (f" and {len(lNames) - 4} more" if len(lNames) > 4 else "")
        sFile, iLine = control.locate(oContext, oFlat, lCells[0])
        return [Finding(sFile, iLine, f"Registers or latches in the top-level module, outside of blocks: {sNames}")]
