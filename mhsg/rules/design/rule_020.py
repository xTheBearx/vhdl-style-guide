# -*- coding: utf-8 -*-

from mhsg.design import graph
from mhsg.design.rule import Finding, Rule

READ_TYPES = {"$memrd", "$memrd_v2"}
WRITE_TYPES = {"$memwr", "$memwr_v2"}
MEMORY_TYPES = {"$mem", "$mem_v2"}
MUX_TYPES = {"$mux", "$pmux"}


class rule_020(Rule):
    """
    This rule reports the outputs of memories that decide a condition: the condition of an if statement or of a
    conditional assignment, or the selector of a case statement, directly or through logic.

    .. NOTE:: This is a design rule. It runs in design analysis.

    A memory location that was never written reads as unknown in simulation. An if statement takes its else branch
    on an unknown condition and a case statement its others choice, while the hardware takes either, so simulation
    hides what the hardware can do. A case statement whose others choice assigns unknown values, :code:`'X'`, keeps
    the unknown in simulation and is not reported. Memories that are never written, which hold constants, are not
    reported either.

    **Violation**

    .. code-block:: vhdl

       data_r <= ram(to_integer(address));
       if data_r(0) = '1' then
    """

    def __init__(self):
        super().__init__()
        self.solution = "Register the memory output and check that it was written, or assign 'X' in the others choice of the case statement"

    def check_design(self, oContext):
        oFlat = oContext.flat()
        if oFlat is None:
            return []
        setWritten = set()
        for oCell in oFlat.cells:
            if oCell.type in WRITE_TYPES:
                setWritten.add((oCell.path, memory_id(oCell)))
            elif oCell.type in MEMORY_TYPES and oCell.parameter("WR_PORTS", 0):
                setWritten.add((oCell.path, memory_id(oCell)))
        dFound = {}
        for oCell in oFlat.cells:
            if oCell.type in READ_TYPES:
                sPort = "DATA"
            elif oCell.type in MEMORY_TYPES:
                sPort = "RD_DATA"
            else:
                continue
            tMemory = (oCell.path, memory_id(oCell))
            if tMemory not in setWritten:
                continue
            sMemory = ".".join(oCell.path + (tMemory[1].lstrip("\\"),))
            for oMux in conditions(oFlat, oCell.connections.get(sPort, [])):
                dFound.setdefault(id(oMux), (oMux, set()))[1].add(sMemory)
        lReturn = []
        for oMux, setMemories in dFound.values():
            sFile, iLine = oContext.locate_cell(oMux)
            sWhat = "a case selector" if oMux.type == "$pmux" else "a condition"
            sMemories = ", ".join(sorted(setMemories))
            sNoun = "memories" if len(setMemories) > 1 else "memory"
            lReturn.append(Finding(sFile, iLine, f"Output of {sNoun} {sMemories} is used in {sWhat}"))
        return lReturn


def conditions(oFlat, lStart):
    """Yields the multiplexers whose select input the nets reach through logic, without a register in between."""
    lWork = [n for n in lStart if graph.is_variable(n)]
    setSeen = set(lWork)
    setFound = set()
    while lWork:
        oNet = lWork.pop()
        for oReader, sPort, _ in oFlat.readers.get(oNet, []):
            if oReader is None or oReader.is_black_box() or graph.is_state(oReader.cell) or oReader.type in graph.SINK_TYPES:
                continue
            if oReader.type in MUX_TYPES and sPort == "S":
                if id(oReader) not in setFound and not unknown_default(oReader):
                    setFound.add(id(oReader))
                    yield oReader
                continue
            for sOutput, lNets in oReader.connections.items():
                if oFlat.direction(oReader, sOutput) != "output":
                    continue
                for oOutput in lNets:
                    if graph.is_variable(oOutput) and oOutput not in setSeen:
                        setSeen.add(oOutput)
                        lWork.append(oOutput)


def memory_id(oCell):
    return str(oCell.cell.get("parameters", {}).get("MEMID", ""))


def unknown_default(oCell):
    """Returns whether a case statement assigns unknown values in its others choice."""
    lDefault = oCell.connections.get("A", [])
    return oCell.type == "$pmux" and bool(lDefault) and all(b == "x" for b in lDefault)
