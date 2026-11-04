# -*- coding: utf-8 -*-

import re

from mhsg.design import graph
from mhsg.design.rule import Finding, Rule

reIndex = re.compile(r"\(\d+\)$")


class rule_021(Rule):
    """
    This rule reports buses with more than **maximum_drivers** tri-state drivers, 5 by default.

    .. NOTE:: This is a design rule. It runs in design analysis.

    Each tri-state driver loads the bus, which slows it down, and makes it harder to check that only one driver
    is enabled at a time. The drivers are counted across the hierarchy, in the flattened design.

    **Violation**

    Six instances that each drive the same bus with :code:`'Z'` when they are not selected.
    """

    def __init__(self):
        super().__init__()
        self.solution = "Use a multiplexer instead of tri-state drivers"
        self.maximum_drivers = 5
        self.configuration.append("maximum_drivers")

    def check_design(self, oContext):
        oFlat = oContext.flat()
        if oFlat is None:
            return []
        dBuses = {}
        for oNet, lDrivers in oFlat.drivers.items():
            lCells = []
            for oCell, _, _ in lDrivers:
                if oCell is not None and graph.is_tristate(oCell.cell) and oCell not in lCells:
                    lCells.append(oCell)
            if len(lCells) <= int(self.maximum_drivers):
                continue
            sBus = reIndex.sub("", oFlat.net_name(oNet))
            iCount, _ = dBuses.get(sBus, (0, []))
            if len(lCells) > iCount:
                dBuses[sBus] = (len(lCells), lCells)
        lReturn = []
        for sBus, (iCount, lCells) in sorted(dBuses.items()):
            sFile, iLine = oContext.locate_cell(lCells[0], sBus.split(".")[-1])
            lReturn.append(Finding(sFile, iLine, f"Bus {sBus} has {iCount} tri-state drivers, more than {self.maximum_drivers}"))
        return lReturn
