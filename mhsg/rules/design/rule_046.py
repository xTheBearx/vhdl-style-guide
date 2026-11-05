# -*- coding: utf-8 -*-

import functools

from mhsg.design import graph
from mhsg.design.rule import Finding, Rule, module_text


class rule_046(Rule):
    """
    This rule reports modules that hold logic between their instances: logic that an output of an instance drives
    and that drives an input of an instance, without a register in between.

    .. NOTE:: This is a design rule. It runs in design analysis. It is disabled by default: it is meant for the parents
              of the blocks on speed-critical paths.

    A module whose instances are connected only by wires keeps each path inside the blocks, where it is synthesized and
    timed with them; logic in the parent adds to paths that cross from one block to the next.

    **Violation**

    .. code-block:: vhdl

       u_b : entity work.b port map (d => a_out and enable, ...);
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.disabled_in_design = True
        self.solution = "Move the logic between the instances into one of the blocks"

    def check_design(self, oContext):
        oNetlist = oContext.netlist
        if oNetlist is None:
            return []
        dModules = oNetlist.modules
        lReturn = []
        for sModule, dModule in sorted(dModules.items()):
            dCells = dModule.get("cells", {})
            setInstances = {s for s, d in dCells.items() if d.get("type") in dModules or not str(d.get("type", "")).startswith("$")}
            if len(setInstances) < 2:
                continue
            setLogic = {s for s, d in dCells.items() if s not in setInstances and not graph.is_state(d) and d.get("type") not in graph.SINK_TYPES}
            dDrivers = {}
            dReaders = {}
            for sCell, dCell in dCells.items():
                for sPort, lBits in dCell.get("connections", {}).items():
                    dTarget = dDrivers if self.direction(dModules, dCell, sPort) == "output" else dReaders
                    for oBit in lBits:
                        if graph.is_variable(oBit):
                            dTarget.setdefault(oBit, []).append(sCell)
            # The logic an instance output reaches, and the logic that reaches an instance input
            setFed = reached(setInstances, setLogic, functools.partial(self.bits, dModules, dCells, True), dReaders)
            setFeeding = reached(setInstances, setLogic, functools.partial(self.bits, dModules, dCells, False), dDrivers)
            lBetween = sorted(setFed & setFeeding)
            if lBetween:
                sFile, iLine = self.locate(oContext, sModule, lBetween)
                sCells = f"{len(lBetween)} cell{'s' if len(lBetween) > 1 else ''}"
                lReturn.append(Finding(sFile, iLine, f"Module {module_text(sModule)} holds logic between its instances ({sCells})"))
        return lReturn

    @staticmethod
    def direction(dModules, dCell, sPort):
        sType = dCell.get("type")
        if sType in dModules:
            return dModules[sType].get("ports", {}).get(sPort, {}).get("direction", "input")
        sDirection = dCell.get("port_directions", {}).get(sPort)
        return sDirection or ("output" if sPort in graph.OUTPUT_PORTS else "input")

    def bits(self, dModules, dCells, bOutputs, sCell):
        """The bits of the outputs of a cell, or of its inputs."""
        dCell = dCells[sCell]
        return [
            b
            for s, l in dCell.get("connections", {}).items()
            if (self.direction(dModules, dCell, s) == "output") == bOutputs
            for b in l
            if graph.is_variable(b)
        ]


def reached(setStarts, setLogic, fBits, dNext):
    """The logic cells reached from the start cells through logic: by their output bits and the readers of those."""
    setReturn = set()
    lWork = list(setStarts)
    while lWork:
        sCell = lWork.pop()
        for oBit in fBits(sCell):
            for sNext in dNext.get(oBit, []):
                if sNext in setLogic and sNext not in setReturn:
                    setReturn.add(sNext)
                    lWork.append(sNext)
    return setReturn
