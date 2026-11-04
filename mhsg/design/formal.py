# -*- coding: utf-8 -*-
"""
Formal reachability of branches with SymbiYosys.

Each branch of the design, a value of the select input of a multiplexer, gets a cover statement in its module, so it
is checked in every instance of the module. One cover run, a bounded search from reset of depth cycles, finds the
branches that can be taken. Each branch it does not reach gets a run of its own that tries to prove it can never be
taken, with abc pdr, within a time limit. A branch is then:

* reachable: the cover run, or the proof, found a way to take it;
* unreachable: the proof shows no way to take it from reset;
* undecided: neither within the time limits.

The design starts from reset: the top inputs that drive asynchronous resets are held active in the first cycle, and
assumptions can hold top inputs at a value in every cycle. Black boxes are taken out and their outputs are free, so
they can take any value in any cycle. Assertions of the design are left out; its assumptions are kept.
"""

import copy
import json
import os
import re
import shutil
import subprocess
import tempfile

from mhsg.design import graph

MUX_TYPES = ("$mux", "$pmux")
RESET_PORTS = {"ARST": "ARST_POLARITY", "SET": "SET_POLARITY", "CLR": "CLR_POLARITY"}
CHECK_TYPES = {"$assert", "$cover", "$live", "$fair", "$check"}
SOURCE_PREFIX = "mhsg_branch_"

reReached = re.compile(r"reached cover statement \S+ at " + SOURCE_PREFIX + r"(\d+)")
# While it runs, smtbmc names the cover cells, which are named after the branches
reReachedCell = re.compile(r"Reached cover statement in step \d+ at \S+ (?:\S*\.)?mhsg_check_(\d+)\b")
reUnreachedHeader = re.compile(r"unreached cover statements:")
reUnreached = re.compile(r"^\s*\S+ at " + SOURCE_PREFIX + r"(\d+)")
reDone = re.compile(r"DONE \((\w+), rc=\d+\)")

REACHABLE = "reachable"
UNREACHABLE = "unreachable"
UNDECIDED = "undecided"


class Branch:
    """A value of the select input of a multiplexer of a module: bits that are 1, or none for the default of a $pmux."""

    def __init__(self, iIndex, sModule, sCell, lSelect, oValue):
        self.index = iIndex
        self.module = sModule
        self.cell = sCell
        # The select bits, and the value: 1 or 0 for a $mux, the index of the bit that is 1 for a $pmux, or None for
        # its default, when no bit is 1
        self.select = lSelect
        self.value = oValue
        self.status = None
        # The cells to locate the branch by: the logic that computes the condition, which is at the condition, then
        # the multiplexer, which GHDL puts at the start of a clocked process
        self.cells = [sCell]

    def describe(self):
        if self.value is None:
            return "the others choice of this case statement is never taken"
        if isinstance(self.value, int) and len(self.select) > 1:
            return "this choice of the case statement is never taken"
        return "this condition is never true" if self.value == 1 else "this condition is never false"


def branches(dModules):
    """Returns the branches of the multiplexers of the modules whose select bits are not constant, one per value."""
    lReturn = []
    for sModule, dModule in sorted(dModules.items()):
        dDrivers = {}
        for sDriver, dDriver in dModule.get("cells", {}).items():
            for sPort, lBits in dDriver.get("connections", {}).items():
                if sPort in ("Y", "Q"):
                    for oBit in lBits:
                        dDrivers.setdefault(oBit, sDriver)
        setSeen = set()
        for sCell, dCell in sorted(dModule.get("cells", {}).items()):
            if dCell.get("type") not in MUX_TYPES:
                continue
            lSelect = dCell.get("connections", {}).get("S", [])
            if not lSelect or not all(graph.is_variable(b) for b in lSelect):
                continue
            if dCell["type"] == "$mux":
                lValues = [1, 0]
            else:
                lValues = list(range(len(lSelect))) + [None]
            for oValue in lValues:
                tKey = (tuple(lSelect), oValue)
                if tKey in setSeen:
                    continue
                setSeen.add(tKey)
                oBranch = Branch(len(lReturn), sModule, sCell, list(lSelect), oValue)
                oBit = lSelect[oValue] if isinstance(oValue, int) and len(lSelect) > 1 else (lSelect[0] if oValue is not None else None)
                if dDrivers.get(oBit) is not None:
                    oBranch.cells.insert(0, dDrivers[oBit])
                lReturn.append(oBranch)
    return lReturn


class Builder:
    """Adds cells to a module of a JSON netlist, with bits numbered after its own."""

    def __init__(self, dModule, sPrefix):
        self.module = dModule
        self.prefix = sPrefix
        self.count = 0
        iMax = 0
        for dNet in dModule.get("netnames", {}).values():
            iMax = max([iMax] + [b for b in dNet.get("bits", []) if isinstance(b, int)])
        for dCell in dModule.get("cells", {}).values():
            for lBits in dCell.get("connections", {}).values():
                iMax = max([iMax] + [b for b in lBits if isinstance(b, int)])
        for dPort in dModule.get("ports", {}).values():
            iMax = max([iMax] + [b for b in dPort.get("bits", []) if isinstance(b, int)])
        self.next = iMax + 1

    def bit(self):
        self.next += 1
        return self.next - 1

    def cell(self, sType, dConnections, dParameters=None, dDirections=None, sSource=None, sName=None):
        self.count += 1
        dCell = {"type": sType, "parameters": dParameters or {}, "attributes": {}, "port_directions": dDirections or {}, "connections": dConnections}
        if sSource:
            dCell["attributes"]["src"] = sSource
        self.module.setdefault("cells", {})[sName or f"{self.prefix}{self.count}"] = dCell
        return dCell

    def unary(self, sType, lA):
        iY = self.bit()
        dParameters = {"A_SIGNED": 0, "A_WIDTH": len(lA), "Y_WIDTH": 1}
        self.cell(sType, {"A": list(lA), "Y": [iY]}, dParameters, {"A": "input", "Y": "output"})
        return iY

    def binary(self, sType, oA, oB):
        iY = self.bit()
        dParameters = {"A_SIGNED": 0, "B_SIGNED": 0, "A_WIDTH": 1, "B_WIDTH": 1, "Y_WIDTH": 1}
        self.cell(sType, {"A": [oA], "B": [oB], "Y": [iY]}, dParameters, {"A": "input", "B": "input", "Y": "output"})
        return iY

    def taken(self, oBranch):
        """The bit that is 1 when a branch is taken."""
        if oBranch.value is None:
            return self.unary("$logic_not", oBranch.select)
        if isinstance(oBranch.value, int) and len(oBranch.select) > 1:
            return oBranch.select[oBranch.value]
        return oBranch.select[0] if oBranch.value == 1 else self.unary("$not", oBranch.select)

    def check(self, sType, oBit, sSource, sName=None):
        self.cell(sType, {"A": [oBit], "EN": ["1"]}, {}, {"A": "input", "EN": "input"}, sSource, sName)


def reset_inputs(oFlat):
    """{(top port, index): active value} for the top inputs that drive asynchronous resets, through inverters."""
    dReturn = {}
    for oCell in oFlat.cells:
        for sPort, sPolarity in RESET_PORTS.items():
            for oNet in oCell.connections.get(sPort, []):
                if not graph.is_variable(oNet):
                    continue
                iActive = 1 if graph.parameter(oCell.cell, sPolarity, 1) else 0
                for _ in range(4):
                    tDriver = oFlat.driver(oNet)
                    if tDriver is None or tDriver[0] is None or tDriver[0].type not in ("$not", "$logic_not"):
                        break
                    oNet = tDriver[0].connections.get("A", [None])[0]
                    iActive = 1 - iActive
                for oDriver, sTop, iIndex in oFlat.drivers.get(oNet, []):
                    if oDriver is None:
                        dReturn.setdefault((sTop, iIndex), iActive)
    return dReturn


def formal_netlist(dNetlist, sTop, lBranches, sCheck, dResets, dAssumptions, setBlackBoxes):
    """
    Returns a copy of the netlist with a check of type sCheck, $cover or $assert, for each branch: $cover that it is
    taken, $assert that it is not. Assertions and covers of the design are left out, and black boxes taken out.
    """
    dReturn = copy.deepcopy(dNetlist)
    dModules = dReturn.get("modules", {})
    for sBox in setBlackBoxes:
        dModules.pop(sBox, None)
    dBuilders = {}
    for sModule, dModule in dModules.items():
        dCells = dModule.get("cells", {})
        for sCell in [s for s, d in dCells.items() if d.get("type") in CHECK_TYPES or d.get("type") in setBlackBoxes]:
            del dCells[sCell]
        dBuilders[sModule] = Builder(dModule, "\\mhsg_formal_")
    for oBranch in lBranches:
        oBuilder = dBuilders.get(oBranch.module)
        if oBuilder is None:
            continue
        iTaken = oBuilder.taken(oBranch)
        if sCheck == "$assert":
            iTaken = oBuilder.unary("$not", [iTaken])
        oBuilder.check(sCheck, iTaken, f"{SOURCE_PREFIX}{oBranch.index}", f"\\mhsg_check_{oBranch.index}")
    oTop = dBuilders.get(sTop)
    if oTop is not None:
        dPorts = oTop.module.get("ports", {})
        iFirst = oTop.bit()
        oTop.cell("$initstate", {"Y": [iFirst]}, {}, {"Y": "output"})
        iLater = oTop.unary("$not", [iFirst])
        for (sPort, iIndex), iActive in sorted(dResets.items()):
            lBits = dPorts.get(sPort, {}).get("bits", [])
            if iIndex >= len(lBits):
                continue
            oActive = lBits[iIndex] if iActive else oTop.unary("$not", [lBits[iIndex]])
            oTop.check("$assume", oTop.binary("$or", iLater, oActive), None)
        for sPort, oValue in sorted(dAssumptions.items()):
            lBits = dPorts.get(sPort, {}).get("bits", [])
            for iIndex, oBit in enumerate(lBits):
                iValue = (int(oValue) >> iIndex) & 1
                oTop.check("$assume", oBit if iValue else oTop.unary("$not", [oBit]), None)
    return dReturn


def sby_text(sTop, sMode, iDepth, iTimeout, bMulticlock):
    lOptions = [f"mode {sMode}", f"depth {iDepth}" if sMode == "cover" else "", f"timeout {iTimeout}", "multiclock on" if bMulticlock else ""]
    sEngine = "smtbmc" if sMode == "cover" else "abc pdr"
    lScript = ["read_json design.json", f"prep -flatten -top {sTop}", "setundef -undriven -anyseq"]
    if not bMulticlock:
        lScript.append("async2sync")
    return (
        "[options]\n"
        + "".join(s + "\n" for s in lOptions if s)
        + f"\n[engines]\n{sEngine}\n\n[script]\n"
        + "".join(s + "\n" for s in lScript)
        + "\n[files]\ndesign.json\n"
    )


def run_sby(sSby, dNetlist, sTop, sMode, iDepth, iTimeout, bMulticlock):
    """Runs SymbiYosys and returns (its result, such as PASS, FAIL or TIMEOUT, or None if it did not finish, its log)."""
    with tempfile.TemporaryDirectory(prefix="mhsg_formal_") as sDirectory:
        with open(os.path.join(sDirectory, "design.json"), "w", encoding="utf-8") as oFile:
            json.dump(dNetlist, oFile)
        sFile = os.path.join(sDirectory, "check.sby")
        with open(sFile, "w", encoding="utf-8") as oFile:
            oFile.write(sby_text(sTop, sMode, iDepth, iTimeout, bMulticlock))
        dEnvironment = dict(os.environ)
        # SymbiYosys runs yosys, yosys-smtbmc and the solvers by name: those beside it
        dEnvironment["PATH"] = os.path.dirname(os.path.realpath(sSby)) + os.pathsep + os.path.dirname(sSby) + os.pathsep + dEnvironment.get("PATH", "")
        try:
            oProcess = subprocess.run(
                [sSby, "-f", sFile],
                cwd=sDirectory,
                capture_output=True,
                text=True,
                env=dEnvironment,
                timeout=iTimeout + 60,
                check=False,
            )
        except subprocess.TimeoutExpired as oError:
            sOut = oError.stdout.decode(errors="replace") if isinstance(oError.stdout, bytes) else (oError.stdout or "")
            return None, sOut
    sLog = oProcess.stdout + oProcess.stderr
    oMatch = None
    for oMatch in reDone.finditer(sLog):
        pass
    return (oMatch.group(1) if oMatch else None), sLog


def cover_results(sLog):
    """Returns the indexes of the branches a cover run reached, also of a run stopped by its time limit."""
    return {int(s) for s in reReached.findall(sLog)} | {int(s) for s in reReachedCell.findall(sLog)}


def is_multiclock(oFlat):
    """Whether the design has latches or more than one clock net, which SymbiYosys needs multiclock for."""
    setClocks = set()
    for oCell in oFlat.cells:
        if oCell.type.startswith("$dlatch") or oCell.type in ("$sr", "$_SR_"):
            return True
        for oNet in oCell.connections.get("CLK", []):
            if graph.is_variable(oNet):
                setClocks.add(oNet)
    return len(setClocks) > 1


def find_sby():
    return shutil.which("sby")


def reachability(sSby, dNetlist, sTop, oFlat, setBlackBoxes, iDepth, iTimeout, iMaximumProofs, dAssumptions, iCoverTimeout=300):
    """
    Returns (the branches with their status, the branches left unchecked as more than iMaximumProofs needed a proof,
    an error text or None).
    """
    lBranches = branches({s: d for s, d in dNetlist.get("modules", {}).items() if s not in setBlackBoxes})
    if not lBranches:
        return [], [], None
    dResets = reset_inputs(oFlat)
    bMulticlock = is_multiclock(oFlat)
    dCover = formal_netlist(dNetlist, sTop, lBranches, "$cover", dResets, dAssumptions, setBlackBoxes)
    sResult, sLog = run_sby(sSby, dCover, sTop, "cover", iDepth, iCoverTimeout, bMulticlock)
    # A cover run stopped by its time limit has reached some branches: the others get proofs
    if sResult not in ("PASS", "FAIL", "TIMEOUT", None):
        return lBranches, [], f"SymbiYosys cover run returned {sResult}"
    setReached = cover_results(sLog)
    lOpen = []
    for oBranch in lBranches:
        if oBranch.index in setReached:
            oBranch.status = REACHABLE
        else:
            lOpen.append(oBranch)
    for oBranch in lOpen[:iMaximumProofs]:
        dProve = formal_netlist(dNetlist, sTop, [oBranch], "$assert", dResets, dAssumptions, setBlackBoxes)
        sResult, _ = run_sby(sSby, dProve, sTop, "prove", iDepth, iTimeout, bMulticlock)
        oBranch.status = {"PASS": UNREACHABLE, "FAIL": REACHABLE}.get(sResult, UNDECIDED)
    return lBranches, lOpen[iMaximumProofs:], None
