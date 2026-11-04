# -*- coding: utf-8 -*-

import json
import os
import subprocess
import tempfile

from mhsg.design import flat, netlist
from mhsg.design.rule import Finding, Rule


class rule_019(Rule):
    """
    This rule reports the registers and output ports of the design reached by a combinational path of more than
    **maximum_levels** levels, 8 by default, after the design is mapped to look-up tables of **lut_size** inputs, 6 by
    default: each register once, with its deepest path.

    .. NOTE:: This is a design rule. It runs in design analysis. It is disabled by default: mapping takes longer than
              the other checks.

    design_007 counts the operators of a path before synthesis, which tells where a path is deep but not how deep it
    is in the device. This rule flattens the design, maps it with Yosys to look-up tables, and counts the tables on
    the paths between registers, memories and the ports of the design, which is closer to the timing of the device.
    Mapping keeps the registers but renames the logic between them, so a finding names the register or port a path
    starts at, when it has a name, and the register it ends at, and is reported at the assignment of that register.

    **Violation**

    A chain of comparisons and multiplexers that maps to more look-up tables than allowed between two registers.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.disabled_in_design = True
        self.solution = "Split the path with a register"
        self.maximum_levels = 8
        self.lut_size = 6
        self.configuration.extend(["maximum_levels", "lut_size"])

    def check_design(self, oContext):
        if oContext.result is None or oContext.result.netlist is None or oContext.tools is None:
            return []
        sTop = flat.top_module(oContext.netlist) if oContext.netlist is not None else None
        if sTop is None:
            return []
        lPaths = mapped_paths(oContext.tools, oContext.result.netlist, sTop, int(self.lut_size))
        if lPaths is None:
            return []
        lReturn = []
        lTopCells = list(oContext.result.netlist["modules"][sTop].get("cells", {}))
        # The registers of the design by the hierarchical name of the signal they drive, to locate a path's end
        oFlat = oContext.flat()
        dRegisters = {}
        for oCell in oFlat.cells if oFlat is not None else []:
            if oCell.type in netlist.FLIP_FLOP_TYPES:
                dRegisters.setdefault(oFlat.cell_name(oCell), oCell)
        for iLevels, sStart, sEnd, sSource in lPaths:
            if iLevels <= int(self.maximum_levels):
                continue
            oLocation = netlist.source_location(sSource, getattr(oContext.netlist, "_setFiles", None)) if sSource else None
            if oLocation is not None:
                sFile, iLine = oContext.refine(oLocation, sEnd.split(".")[-1])
            elif sEnd in dRegisters:
                sFile, iLine = oContext.locate_cell(dRegisters[sEnd], sEnd.split(".")[-1])
            else:
                sFile, iLine = self.locate(oContext, sTop, lTopCells)
            sFrom = f" from {sStart}" if sStart else ""
            sMessage = f"Path of {iLevels} levels of {self.lut_size}-input look-up tables after mapping{sFrom} to {sEnd}, more than {self.maximum_levels}"
            lReturn.append(Finding(sFile, iLine, sMessage))
        return lReturn


def mapped_paths(oTools, dNetlist, sTop, iLutSize):
    """
    Maps the design to look-up tables and returns [(levels, start, end, source)] for each register and output port:
    the most look-up tables on a path to it, the register or input the path starts at, its own name, and the src
    attribute of the register; or None if Yosys fails. A register is named once, with its deepest bit.
    """
    with tempfile.TemporaryDirectory(prefix="mhsg_mapped_") as sDirectory:
        sJson = os.path.join(sDirectory, "design.json")
        sMapped = os.path.join(sDirectory, "mapped.json")
        with open(sJson, "w", encoding="utf-8") as oFile:
            json.dump(dNetlist, oFile)
        sScript = (
            f"read_json {sJson}; hierarchy -top {sTop}; flatten; synth -run coarse; opt; techmap; opt; " f"abc -lut {iLutSize}; opt_clean; write_json {sMapped}"
        )
        oProcess = subprocess.run([oTools.yosys, "-p", sScript], capture_output=True, text=True, env=oTools.environment, check=False)
        if oProcess.returncode != 0 or not os.path.isfile(sMapped):
            return None
        with open(sMapped, encoding="utf-8") as oFile:
            dMapped = json.load(oFile)
    dModule = dMapped.get("modules", {}).get(sTop)
    if dModule is None:
        return None
    return LutGraph(dModule).paths()


class LutGraph:
    """The look-up tables of a flat mapped module, with the depth of each net in tables."""

    def __init__(self, dModule):
        self.module = dModule
        self.cells = dModule.get("cells", {})
        self.drivers = {}
        for sCell, dCell in self.cells.items():
            for sPort, sDirection in dCell.get("port_directions", {}).items():
                if sDirection == "output":
                    for oBit in dCell.get("connections", {}).get(sPort, []):
                        if isinstance(oBit, int):
                            self.drivers[oBit] = sCell
        self.names = {}
        for sName, dNet in sorted(dModule.get("netnames", {}).items(), key=lambda t: (t[1].get("hide_name", 0), t[0].startswith("$"), len(t[0]))):
            lBits = dNet.get("bits", [])
            for iIndex, oBit in enumerate(lBits):
                if isinstance(oBit, int) and oBit not in self.names:
                    sClean = sName.lstrip("\\")
                    self.names[oBit] = (sClean, f"{sClean}({iIndex})" if len(lBits) > 1 else sClean)
        self._dDepths = {}

    def depth(self, oBit):
        """(look-up tables on the deepest path to a net, the net that path starts at)."""
        if not isinstance(oBit, int):
            return 0, None
        lStack = [oBit]
        while lStack:
            oTop = lStack[-1]
            if oTop in self._dDepths:
                lStack.pop()
                continue
            sCell = self.drivers.get(oTop)
            dCell = self.cells.get(sCell) if sCell is not None else None
            if dCell is None or dCell.get("type") != "$lut":
                self._dDepths[oTop] = (0, oTop)
                lStack.pop()
                continue
            lInputs = [b for b in dCell.get("connections", {}).get("A", []) if isinstance(b, int)]
            lPending = [b for b in lInputs if b not in self._dDepths and b not in lStack]
            if lPending:
                lStack.extend(lPending)
                continue
            # An input still on the stack closes a combinational loop: it counts as a start
            lDepths = [self._dDepths.get(b, (0, b)) for b in lInputs]
            iLevels, oStart = max(lDepths, key=lambda t: t[0]) if lDepths else (0, oTop)
            self._dDepths[oTop] = (iLevels + 1, oStart)
            lStack.pop()
        return self._dDepths[oBit]

    def name(self, oBit):
        """The name of a net, or "" for one Yosys named, such as u_alu.2165.B, whose name tells nothing."""
        sName = self.names.get(oBit, ("", ""))[1] if oBit is not None else ""
        if any(s.isdigit() or s.startswith("$") for s in sName.split("(")[0].split(".")):
            return ""
        return sName

    def paths(self):
        dWorst = {}
        for sCell, dCell in self.cells.items():
            if dCell.get("type") == "$lut":
                continue
            lQ = [b for sPort, s in dCell.get("port_directions", {}).items() if s == "output" for b in dCell.get("connections", {}).get(sPort, [])]
            sEnd = self.names.get(lQ[0], (sCell.lstrip("\\"), ""))[0] if lQ and isinstance(lQ[0], int) else sCell.lstrip("\\")
            for sPort, sDirection in dCell.get("port_directions", {}).items():
                if sDirection != "input":
                    continue
                for oBit in dCell.get("connections", {}).get(sPort, []):
                    iLevels, oStart = self.depth(oBit)
                    if iLevels > dWorst.get(sEnd, (-1,))[0]:
                        dWorst[sEnd] = (iLevels, self.name(oStart), dCell.get("attributes", {}).get("src", ""))
        for sPort, dPort in self.module.get("ports", {}).items():
            if dPort.get("direction") not in ("output", "inout"):
                continue
            for oBit in dPort.get("bits", []):
                iLevels, oStart = self.depth(oBit)
                if iLevels > dWorst.get(sPort, (-1,))[0]:
                    dWorst[sPort] = (iLevels, self.name(oStart), "")
        return sorted(((t[0], t[1], sEnd, t[2]) for sEnd, t in dWorst.items()), key=lambda t: (-t[0], t[2]))
