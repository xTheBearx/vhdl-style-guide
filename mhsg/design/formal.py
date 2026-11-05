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

import concurrent.futures
import copy
import json
import os
import re
import shutil
import subprocess
import tempfile

from mhsg.design import fsm, graph

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

    def build(self, oBuilder):
        """Adds the logic of the check to a module, and returns the bit that is 1 when the branch is taken."""
        return oBuilder.taken(self)

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
                if only_unknown(dCell, oValue):
                    # A branch that selects unknown values is how synthesis writes values never meant to occur, such
                    # as the others choice of a case statement on a state that assigns 'X', or the encodings no
                    # state uses: not a branch of the code
                    continue
                tKey = (tuple(lSelect), oValue)
                if tKey in setSeen:
                    continue
                setSeen.add(tKey)
                oBranch = Branch(len(lReturn), sModule, sCell, list(lSelect), oValue)
                oBit = lSelect[oValue] if isinstance(oValue, int) and len(lSelect) > 1 else (lSelect[0] if oValue is not None else None)
                sDriver = dDrivers.get(oBit)
                if sDriver is not None and not graph.is_state(dModule["cells"][sDriver]):
                    oBranch.cells.insert(0, sDriver)
                lReturn.append(oBranch)
    return lReturn


def only_unknown(dCell, oValue):
    """Whether the data a branch of a multiplexer selects is unknown, 'x', in every bit."""
    dConnections = dCell.get("connections", {})
    lA = dConnections.get("A", [])
    lB = dConnections.get("B", [])
    if dCell.get("type") == "$mux":
        lData = lB if oValue == 1 else lA
    elif oValue is None:
        lData = lA
    else:
        iWidth = len(lA) or 1
        lData = lB[oValue * iWidth : (oValue + 1) * iWidth]
    return bool(lData) and all(b == "x" for b in lData)


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

    def initstate(self):
        """The bit that is 1 in the first cycle only, made once per module."""
        if getattr(self, "_iInitstate", None) is None:
            self._iInitstate = self.bit()
            self.cell("$initstate", {"Y": [self._iInitstate]}, {}, {"Y": "output"})
        return self._iInitstate

    def equals(self, lBits, iValue):
        """The bit that is 1 when a word has a value."""
        iY = self.bit()
        lValue = ["1" if (iValue >> i) & 1 else "0" for i in range(len(lBits))]
        dParameters = {"A_SIGNED": 0, "B_SIGNED": 0, "A_WIDTH": len(lBits), "B_WIDTH": len(lBits), "Y_WIDTH": 1}
        self.cell("$eq", {"A": list(lBits), "B": lValue, "Y": [iY]}, dParameters, {"A": "input", "B": "input", "Y": "output"})
        return iY

    def flag(self, oClockBit, iPolarity, oSet):
        """
        A register that is 1 from the clock edge after oSet is 1, and 0 before: the first cycle resets it
        asynchronously, which also holds in multiclock mode, where a step need not be a clock edge.
        """
        iQ = self.bit()
        iD = self.binary("$or", iQ, oSet)
        dParameters = {"WIDTH": 1, "CLK_POLARITY": iPolarity, "ARST_POLARITY": 1, "ARST_VALUE": "0"}
        dDirections = {"CLK": "input", "ARST": "input", "D": "input", "Q": "output"}
        self.cell("$adff", {"CLK": [oClockBit], "ARST": [self.initstate()], "D": [iD], "Q": [iQ]}, dParameters, dDirections)
        return iQ

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


def formal_netlist(dNetlist, sTop, lBranches, sCheck, dResets, dAssumptions, setBlackBoxes, bReleased=False):
    """
    Returns a copy of the netlist with a check of type sCheck, $cover or $assert, for each branch: $cover that it is
    taken, $assert that it is not. Assertions and covers of the design are left out, and black boxes taken out. The
    resets are active in the first cycle; with bReleased, they are inactive in all the others.
    """
    dReturn = copy.deepcopy(dNetlist)
    dModules = dReturn.get("modules", {})
    for sBox in setBlackBoxes:
        dModules.pop(sBox, None)
    dBuilders = {}
    for sModule, dModule in dModules.items():
        remove_empty(dModule)
        dCells = dModule.get("cells", {})
        for sCell in [s for s, d in dCells.items() if d.get("type") in CHECK_TYPES or d.get("type") in setBlackBoxes]:
            del dCells[sCell]
        dBuilders[sModule] = Builder(dModule, "\\mhsg_formal_")
        free_released(dModule, dBuilders[sModule])
        latch_looped_multiplexers(dModule)
    for oBranch in lBranches:
        oBuilder = dBuilders.get(oBranch.module)
        if oBuilder is None:
            continue
        iTaken = oBranch.build(oBuilder)
        if sCheck == "$assert":
            iTaken = oBuilder.unary("$not", [iTaken])
        oBuilder.check(sCheck, iTaken, f"{SOURCE_PREFIX}{oBranch.index}", f"\\mhsg_check_{oBranch.index}")
    oTop = dBuilders.get(sTop)
    if oTop is not None:
        dPorts = oTop.module.get("ports", {})
        iFirst = oTop.initstate()
        iLater = oTop.unary("$not", [iFirst])
        for (sPort, iIndex), iActive in sorted(dResets.items()):
            lBits = dPorts.get(sPort, {}).get("bits", [])
            if iIndex >= len(lBits):
                continue
            oActive = lBits[iIndex] if iActive else oTop.unary("$not", [lBits[iIndex]])
            oTop.check("$assume", oTop.binary("$or", iLater, oActive), None)
            if bReleased:
                oTop.check("$assume", oTop.binary("$or", iFirst, oTop.unary("$not", [oActive])), None)
        for sPort, oValue in sorted(dAssumptions.items()):
            lBits = dPorts.get(sPort, {}).get("bits", [])
            for iIndex, oBit in enumerate(lBits):
                iValue = (int(oValue) >> iIndex) & 1
                oTop.check("$assume", oBit if iValue else oTop.unary("$not", [oBit]), None)
    return dReturn


def free_released(dModule, oBuilder):
    """
    Replaces the high impedance bits that cells select, such as a tri-state driver of a bidirectional pin that releases
    it, and the output of tri-state buffers when disabled, with bits that no cell drives, which can take any value: a released pin reads what a pull-up or another device
    drives. Without this, a design that reads back its open-drain pins, such as an I2C master, sees them stuck.
    """
    for dCell in dModule.get("cells", {}).values():
        if dCell.get("type") in ("$tribuf", "$_TBUF_"):
            # A tri-state buffer, which the formal tools do not support: its input when enabled, else any value
            dConnections = dCell["connections"]
            iWidth = len(dConnections.get("Y", []))
            dCell["type"] = "$mux"
            dCell["parameters"] = {"WIDTH": iWidth}
            dCell["port_directions"] = {"A": "input", "B": "input", "S": "input", "Y": "output"}
            dCell["connections"] = {"A": [oBuilder.bit() for _ in range(iWidth)], "B": dConnections["A"], "S": dConnections["EN"], "Y": dConnections["Y"]}
            continue
        dDirections = dCell.get("port_directions", {})
        for sPort, lBits in dCell.get("connections", {}).items():
            if dDirections.get(sPort, "input") != "output" and "z" in lBits:
                dCell["connections"][sPort] = [oBuilder.bit() if b == "z" else b for b in lBits]


def looped_bits(dCell):
    """
    For a $mux whose output feeds back to a data input, as the GHDL plugin builds some latches, the indexes of the
    looped bits with the port they loop through, A or B; empty for other cells.
    """
    if dCell.get("type") != "$mux":
        return []
    dConnections = dCell.get("connections", {})
    lA, lB, lY = dConnections.get("A", []), dConnections.get("B", []), dConnections.get("Y", [])
    lReturn = []
    for iIndex, oBit in enumerate(lY):
        if not graph.is_variable(oBit):
            continue
        if iIndex < len(lA) and lA[iIndex] == oBit:
            lReturn.append((iIndex, "A"))
        elif iIndex < len(lB) and lB[iIndex] == oBit:
            lReturn.append((iIndex, "B"))
    return lReturn


def has_looped_multiplexers(dNetlist):
    return any(looped_bits(d) for dModule in dNetlist.get("modules", {}).values() for d in dModule.get("cells", {}).values())


def latch_looped_multiplexers(dModule):
    """
    Replaces the looped bits of multiplexers, latches as the GHDL plugin builds them, with $dlatch cells: the formal
    tools see the loop as a combinational loop. A bit that keeps its value when the select is 0 is enabled by 1.
    """
    dCells = dModule.get("cells", {})
    for sCell in [s for s, d in dCells.items() if looped_bits(d)]:
        dCell = dCells[sCell]
        dConnections = dCell["connections"]
        oSelect = dConnections["S"][0]
        for iIndex, sPort in looped_bits(dCell):
            oData = dConnections["B" if sPort == "A" else "A"][iIndex]
            dCells[f"{sCell}_mhsg_latch_{iIndex}"] = {
                "type": "$dlatch",
                "parameters": {"WIDTH": 1, "EN_POLARITY": 1 if sPort == "A" else 0},
                "attributes": dict(dCell.get("attributes", {})),
                "port_directions": {"EN": "input", "D": "input", "Q": "output"},
                "connections": {"EN": [oSelect], "D": [oData], "Q": [dConnections["Y"][iIndex]]},
            }
        setLooped = {i for i, _ in looped_bits(dCell)}
        lKept = [i for i in range(len(dConnections["Y"])) if i not in setLooped]
        if not lKept:
            del dCells[sCell]
            continue
        for sPort in ("A", "B", "Y"):
            dConnections[sPort] = [dConnections[sPort][i] for i in lKept]
        dCell.setdefault("parameters", {})["WIDTH"] = len(lKept)


def remove_empty(dModule):
    """
    Removes the ports and nets of no bits of a module, and the connections of no bits of its cells: a generic can make
    a port empty, and the SMT-LIB that SymbiYosys writes for one names a term it never declares.
    """
    for sKey in ("ports", "netnames"):
        dItems = dModule.get(sKey, {})
        for sName in [s for s, d in dItems.items() if not d.get("bits")]:
            del dItems[sName]
    for dCell in dModule.get("cells", {}).values():
        dConnections = dCell.get("connections", {})
        for sPort in [s for s, l in dConnections.items() if not l]:
            del dConnections[sPort]
            dCell.get("port_directions", {}).pop(sPort, None)


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
    bMulticlock = is_multiclock(oFlat) or has_looped_multiplexers(dNetlist)
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

    def prove(oBranch):
        dProve = formal_netlist(dNetlist, sTop, [oBranch], "$assert", dResets, dAssumptions, setBlackBoxes)
        sResult, _ = run_sby(sSby, dProve, sTop, "prove", iDepth, iTimeout, bMulticlock)
        oBranch.status = {"PASS": UNREACHABLE, "FAIL": REACHABLE}.get(sResult, UNDECIDED)

    # The proofs are independent: one SymbiYosys run each, as many at a time as there are processors
    lProofs = lOpen[:iMaximumProofs]
    if lProofs:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(len(lProofs), os.cpu_count() or 1))) as oPool:
            list(oPool.map(prove, lProofs))
    return lBranches, lOpen[iMaximumProofs:], None


ENTERED = "entered"
RETURNS = "returns"


class StateCheck:
    """
    A check of a state of a state machine: that the machine enters it (ENTERED), or that it returns to its reset
    state after it (RETURNS). Neither counts the first cycle, in which the state of a register without an asynchronous
    reset is not known yet.
    """

    def __init__(self, iIndex, oMachine, iValue, sKind):
        self.index = iIndex
        self.machine = oMachine
        self.module = oMachine.module
        self.value = iValue
        self.kind = sKind
        self.status = None

    def build(self, oBuilder):
        iLater = oBuilder.unary("$not", [oBuilder.initstate()])
        iIn = oBuilder.binary("$and", oBuilder.equals(self.machine.bits, self.value), iLater)
        if self.kind == ENTERED:
            return iIn
        iSeen = oBuilder.flag(self.machine.clock, self.machine.clock_polarity, iIn)
        iBack = oBuilder.binary("$and", oBuilder.equals(self.machine.bits, self.machine.reset), iLater)
        return oBuilder.binary("$and", iSeen, iBack)


def trace_input(oFlat, oNet, iActive, dResets):
    """
    Returns (top input, index, active value) for a net driven by a top input through inverters, or True when a
    register drives it that an asynchronous reset in dResets sets to the active value, which a reset synchronizer
    does; None otherwise.
    """
    for _ in range(8):
        if not graph.is_variable(oNet):
            return None
        for oDriver, sTop, iIndex in oFlat.drivers.get(oNet, []):
            if oDriver is None:
                return (sTop, iIndex, iActive)
        tDriver = oFlat.driver(oNet)
        if tDriver is None or tDriver[0] is None:
            return None
        oCell = tDriver[0]
        if oCell.type in ("$not", "$logic_not"):
            iActive = 1 - iActive
        elif oCell.type not in ("$pos", "$buf"):
            if oCell.type in ("$adff", "$adffe") and reset_value_active(oFlat, oCell, tDriver[2], iActive, dResets):
                return True
            return None
        oNet = oCell.connections.get("A", [None])[0]
    return None


def reset_value_active(oFlat, oCell, iIndex, iActive, dResets):
    """Whether a register bit with an asynchronous reset from a top input in dResets holds the active value at reset."""
    oReset = (oCell.connections.get("ARST") or [None])[0]
    tReset = trace_input(oFlat, oReset, graph.parameter(oCell.cell, "ARST_POLARITY", 1), {})
    if not isinstance(tReset, tuple) or dResets.get(tReset[:2]) != tReset[2]:
        return False
    return (graph.parameter(oCell.cell, "ARST_VALUE", 0) >> iIndex) & 1 == iActive


def started_machines(oFlat, lMachines, dResets):
    """
    Returns (the state machines that start from their reset state in at least one instance, {(top input, index):
    active value} for the synchronous resets that need holding in the first cycle). A state machine with an
    asynchronous reset starts from it when a top input in dResets drives the reset; one with a synchronous reset when a
    top input drives it, or a register that an asynchronous reset sets, as a reset synchronizer does, for either.
    """
    dFlat = {(tuple(o.path), o.module, o.name): o for o in oFlat.cells}
    dSync = {}
    lReturn = []
    for oMachine in lMachines:
        bStarted = False
        for oCell in oFlat.cells:
            if oCell.module != oMachine.module or oCell.name != oMachine.cell:
                continue
            if oMachine.asynchronous:
                oReset = (oCell.connections.get("ARST") or [None])[0]
                tReset = trace_input(oFlat, oReset, graph.parameter(oCell.cell, "ARST_POLARITY", 1), dResets)
                bStarted = bStarted or tReset is True or (isinstance(tReset, tuple) and dResets.get(tReset[:2]) == tReset[2])
            elif oMachine.reset_select is not None:
                sMux, iActive, _ = oMachine.reset_select
                oMux = dFlat.get((tuple(oCell.path), oCell.module, sMux))
                sPort = "SRST" if sMux == oMachine.cell else "S"
                oSelect = (oMux.connections.get(sPort) or [None])[0] if oMux is not None else None
                tReset = trace_input(oFlat, oSelect, iActive, dResets)
                if isinstance(tReset, tuple):
                    dSync.setdefault(tReset[:2], tReset[2])
                    bStarted = True
                elif tReset is True:
                    bStarted = True
        if bStarted:
            if oMachine.reset is None:
                oMachine.reset = oMachine.reset_select[2]
                oMachine.states.setdefault(oMachine.reset, [])
            lReturn.append(oMachine)
    return lReturn, dSync


def state_machine_checks(sSby, dNetlist, sTop, oFlat, setBlackBoxes, iDepth, iTimeout, iMaximumProofs, dAssumptions, iCoverTimeout=300):
    """
    Checks the states of the state machines of the design, see fsm.py: whether each state can be entered from reset,
    and whether the machine can return to its reset state after it. One cover run searches depth cycles from reset;
    a state it does not enter, or a return it does not find, gets a proof of its own, the states first, at most
    iMaximumProofs in all. Sets the entered and returns dicts of each machine to REACHABLE, UNREACHABLE or UNDECIDED
    by state, None for a check not made. Returns (the state machines checked, the number of checks left without a
    proof as more than iMaximumProofs needed one, an error text or None).
    """
    lMachines = fsm.state_machines({s: d for s, d in dNetlist.get("modules", {}).items() if s not in setBlackBoxes})
    if not lMachines:
        return [], 0, None
    dResets = reset_inputs(oFlat)
    lMachines, dSync = started_machines(oFlat, lMachines, dResets)
    if not lMachines:
        return [], 0, None
    dStart = dict(dResets)
    for tKey, iActive in dSync.items():
        dStart.setdefault(tKey, iActive)
    lChecks = []
    for oMachine in lMachines:
        for iValue in oMachine.other_states():
            for sKind in (ENTERED, RETURNS):
                lChecks.append(StateCheck(len(lChecks), oMachine, iValue, sKind))
    bMulticlock = is_multiclock(oFlat) or has_looped_multiplexers(dNetlist)
    # A reset brings every state machine back to its reset state: the resets are released after the first cycle
    dCover = formal_netlist(dNetlist, sTop, lChecks, "$cover", dStart, dAssumptions, setBlackBoxes, True)
    sResult, sLog = run_sby(sSby, dCover, sTop, "cover", iDepth, iCoverTimeout, bMulticlock)
    if sResult not in ("PASS", "FAIL", "TIMEOUT", None):
        return lMachines, 0, f"SymbiYosys cover run returned {sResult}"
    setReached = cover_results(sLog)
    for oCheck in lChecks:
        if oCheck.index in setReached:
            oCheck.status = REACHABLE

    def prove(oCheck):
        dProve = formal_netlist(dNetlist, sTop, [oCheck], "$assert", dStart, dAssumptions, setBlackBoxes, True)
        sResult, _ = run_sby(sSby, dProve, sTop, "prove", iDepth, iTimeout, bMulticlock)
        oCheck.status = {"PASS": UNREACHABLE, "FAIL": REACHABLE}.get(sResult, UNDECIDED)

    iBudget = iMaximumProofs
    iLeft = 0
    dEntered = {(id(o.machine), o.value): o for o in lChecks if o.kind == ENTERED}
    # The states first: the return of a state that is not entered is not checked
    for sKind in (ENTERED, RETURNS):
        lOpen = [o for o in lChecks if o.kind == sKind and o.status is None]
        if sKind == RETURNS:
            lOpen = [o for o in lOpen if dEntered[(id(o.machine), o.value)].status == REACHABLE]
        lProofs = lOpen[:iBudget]
        iLeft += len(lOpen) - len(lProofs)
        iBudget -= len(lProofs)
        if lProofs:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(len(lProofs), os.cpu_count() or 1))) as oPool:
                list(oPool.map(prove, lProofs))
    for oCheck in lChecks:
        dResults = oCheck.machine.entered if oCheck.kind == ENTERED else oCheck.machine.returns
        dResults[oCheck.value] = oCheck.status
    return lMachines, iLeft, None
