# -*- coding: utf-8 -*-

import fnmatch

from mhsg.design import cdc, graph
from mhsg.design.rule import Finding, Rule

IO_CELLS = [
    # AMD Xilinx
    "IBUF*",
    "OBUF*",
    "IOBUF*",
    # Altera
    "alt_inbuf*",
    "alt_outbuf*",
    "alt_iobuf*",
    # Microchip
    "INBUF*",
    "OUTBUF*",
    "BIBUF*",
    "TRIBUFF*",
    # Lattice
    "IB",
    "IBPU",
    "IBPD",
    "OB",
    "OBZ",
    "OBZPU",
    "BB",
    "BBPU",
    "BBPD",
]


class rule_037(Rule):
    """
    This rule reports I/O cells instantiated below the top level, other than in a block that holds only I/O cells.

    .. NOTE:: This is a design rule. It runs in design analysis. It is disabled by default: a design need not follow
              it.

    I/O cells are black boxes whose type matches one of **io_cells**, file-name style patterns, by default the input,
    output and bidirectional buffers of AMD Xilinx, Altera, Microchip and Lattice, and that connect to a port of the top
    level. Kept in the top level or in a block of their own, they are found and changed in one place, for a new package
    or a new chip, and the blocks stay free of the technology.

    **Violation**

    An IBUFDS instantiated in a receiver block that also holds its logic.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.disabled_in_design = True
        self.io_cells = list(IO_CELLS)
        self.configuration.append("io_cells")
        self.solution = "Instantiate I/O cells in the top level or in an I/O block"

    def check_design(self, oContext):
        oFlat = oContext.flat()
        if oFlat is None:
            return []
        setTopNets = {b for _, lNets in oFlat.top_ports.values() for b in lNets if graph.is_variable(b)}
        lIoCells = [o for o in oFlat.cells if self.is_io_cell(o, setTopNets)]
        setIo = {id(o) for o in lIoCells}
        # A block of its own: an instance under the top level whose black boxes are all I/O cells, with no registers
        dPure = {}
        for oCell in oFlat.cells:
            if not oCell.path:
                continue
            sBlock = oCell.path[0]
            bOther = (oCell.is_black_box() and id(oCell) not in setIo) or cdc.is_clocked(oCell) or oCell.type in graph.STATE_TYPES
            dPure[sBlock] = dPure.get(sBlock, True) and not bOther
        lReturn = []
        for oCell in lIoCells:
            if not oCell.path or dPure.get(oCell.path[0]):
                continue
            sFile, iLine = oContext.locate_cell(oCell)
            sWhere = ".".join(oCell.path)
            lReturn.append(Finding(sFile, iLine, f"I/O cell {oCell!r} ({oCell.type}) is in instance {sWhere}, not in the top level or in a block of I/O cells"))
        return lReturn

    def is_io_cell(self, oCell, setTopNets):
        if not oCell.is_black_box():
            return False
        sType = oCell.type.lstrip("\\").lower()
        if not any(fnmatch.fnmatchcase(sType, str(s).lower()) for s in self.io_cells or []):
            return False
        return any(b in setTopNets for lNets in oCell.connections.values() for b in lNets)
