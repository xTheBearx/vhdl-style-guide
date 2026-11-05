# -*- coding: utf-8 -*-
"""
State machines of a netlist, for the formal checks of their states, see formal.py.

A state machine is a register of two or more bits whose next value only ever is a constant or its own value: the
multiplexers in front of its data input select among constants, the states, and the register itself. Registers whose
next value is computed, such as counters, are not state machines. Its reset state is the value an asynchronous reset
loads, or the constant a synchronous reset loads: the multiplexer nearest the register when its select comes from a
top input, see formal.state_machine_checks.

The states are numbered as the netlist encodes them. The names of the states are taken from the enumerated type of
the signal in the VHDL, whose values GHDL numbers in order, or from the enum_value attributes Yosys writes for
SystemVerilog enumerations.
"""

import math
import os
import re

from mhsg.design import graph

REGISTER_TYPES = ("$dff", "$adff", "$sdff", "$dffe", "$adffe", "$sdffe", "$sdffce")
FOLLOWED_TYPES = ("$pos", "$buf")
MINIMUM_STATES = 3


COMPARE_TYPES = ("$eq", "$ne", "$eqx", "$nex")


class StateMachine:
    """A state register of a module, or a slice of one, such as a field of a record, with its states."""

    def __init__(self, sModule, sCell, sSignal, dCell, lIndexes):
        self.module = sModule
        self.cell = sCell
        dConnections = dCell.get("connections", {})
        lQ = dConnections.get("Q", [])
        # The signal of the register, and the bits of it that hold the state
        self.signal = sSignal
        self.indexes = list(lIndexes)
        self.name = sSignal if len(lIndexes) == len(lQ) else f"{sSignal}[{max(lIndexes)}:{min(lIndexes)}]"
        self.bits = [lQ[i] for i in lIndexes]
        self.clock = (dConnections.get("CLK") or [None])[0]
        self.clock_polarity = graph.parameter(dCell, "CLK_POLARITY", 1)
        # state value -> the cells that load it, by which the state is located
        self.states = {}
        self.reset = None
        # (cell, active value, state value) of the multiplexer nearest the register that loads a constant, which is
        # the synchronous reset when its select comes from a top input, or of the register itself for $sdff
        self.reset_select = None
        self.asynchronous = False
        # state value -> name, when the source tells
        self.names = {}
        # The results of formal.state_machine_checks, by state value
        self.entered = {}
        self.returns = {}

    def state_name(self, iValue):
        return self.names.get(iValue, str(iValue))

    def other_states(self):
        """The states other than the reset state, in order."""
        return [i for i in sorted(self.states) if i != self.reset]


def word_value(lWord):
    """The value of a constant word, its bits from the least significant, or None if a bit is not 0 or 1."""
    if not all(b in ("0", "1") for b in lWord):
        return None
    return sum(1 << i for i, b in enumerate(lWord) if b == "1")


def state_machines(dModules, iMinimumStates=MINIMUM_STATES):
    """
    Returns the StateMachines of the modules, a dict of module name to module of a JSON netlist: whole registers, and
    the slices of registers that are compared with constants, as a case statement on a field of a record does.
    """
    lReturn = []
    for sModule, dModule in sorted(dModules.items()):
        dCells = dModule.get("cells", {})
        dDrivers = {}
        dRegisterBits = {}
        for sCell, dCell in dCells.items():
            for sPort, lBits in dCell.get("connections", {}).items():
                if sPort in ("Y", "Q"):
                    for iIndex, oBit in enumerate(lBits):
                        if graph.is_variable(oBit):
                            dDrivers.setdefault(oBit, (sCell, sPort, iIndex))
            if dCell.get("type") in REGISTER_TYPES:
                for iIndex, oBit in enumerate(dCell.get("connections", {}).get("Q", [])):
                    if graph.is_variable(oBit):
                        dRegisterBits[oBit] = (sCell, iIndex)
        dSlices = {}
        for sCell, dCell in dCells.items():
            if dCell.get("type") in REGISTER_TYPES:
                dSlices.setdefault(sCell, set()).add(tuple(range(len(dCell.get("connections", {}).get("Q", [])))))
            elif dCell.get("type") in COMPARE_TYPES:
                dConnections = dCell.get("connections", {})
                for lWord, lOther in ((dConnections.get("A", []), dConnections.get("B", [])), (dConnections.get("B", []), dConnections.get("A", []))):
                    lRegisters = [dRegisterBits.get(b) for b in lWord]
                    if len(lWord) >= 2 and None not in lRegisters and len({t[0] for t in lRegisters}) == 1 and word_value(lOther) is not None:
                        dSlices.setdefault(lRegisters[0][0], set()).add(tuple(t[1] for t in lRegisters))
        for sCell in sorted(dSlices):
            dCell = dCells[sCell]
            for tIndexes in sorted(dSlices[sCell], key=lambda t: (-len(t), t)):
                if any(set(tIndexes) & set(o.indexes) for o in lReturn if o.module == sModule and o.cell == sCell):
                    continue
                oMachine = machine(sModule, dModule, sCell, dCell, dDrivers, list(tIndexes))
                if oMachine is not None and len(oMachine.states) >= iMinimumStates:
                    lReturn.append(oMachine)
    return lReturn


def follow(dDriver, sType, iIndex):
    """The bits a multiplexer or buffer selects among for a bit of its output: [(port, bit)], or None."""
    dPorts = dDriver.get("connections", {})
    lA, lB = dPorts.get("A", []), dPorts.get("B", [])
    if sType in FOLLOWED_TYPES or sType == "$mux":
        if iIndex >= len(lA):
            return None
        return [("A", lA[iIndex])] + ([("B", lB[iIndex])] if sType == "$mux" else [])
    if sType == "$pmux":
        iWidth = len(lA)
        return [("A", lA[iIndex])] + [("B", lB[k * iWidth + iIndex]) for k in range(len(lB) // iWidth if iWidth else 0)]
    return None


def machine(sModule, dModule, sCell, dCell, dDrivers, lIndexes):
    """
    Returns the StateMachine of bits of a register, or None if their next value is not only constants and their own
    value.
    """
    dConnections = dCell.get("connections", {})
    lQ = dConnections.get("Q", [])
    lD = dConnections.get("D", [])
    if len(lIndexes) < 2 or len(lD) != len(lQ) or not all(graph.is_variable(lQ[i]) for i in lIndexes):
        return None
    oMachine = StateMachine(sModule, sCell, register_name(dModule, lQ) or sCell.lstrip("\\"), dCell, lIndexes)
    lOwn = oMachine.bits
    lWork = [([lD[i] for i in lIndexes], sCell, True)]
    setSeen = set()
    while lWork:
        lWord, sLoader, bNearest = lWork.pop()
        iValue = word_value(lWord)
        if iValue is not None:
            oMachine.states.setdefault(iValue, [])
            if sLoader not in oMachine.states[iValue]:
                oMachine.states[iValue].append(sLoader)
            continue
        if all(b == "x" for b in lWord) or lWord == lOwn:
            continue
        tWord = tuple(lWord)
        if tWord in setSeen:
            continue
        setSeen.add(tWord)
        lDrivers = [dDrivers.get(b) for b in lWord]
        if None in lDrivers or len({t[0] for t in lDrivers}) != 1:
            return None
        sDriver = lDrivers[0][0]
        dDriver = dModule["cells"][sDriver]
        sType = dDriver.get("type")
        lInputs = [follow(dDriver, sType, t[2]) for t in lDrivers]
        if None in lInputs:
            return None
        # The words the driver selects among, one per input: A, the B of a $mux, or each choice of a $pmux
        lWords = [[l[k][1] for l in lInputs] for k in range(len(lInputs[0]))]
        bLoads = sType != "$pmux" and any(word_value(l) is not None for l in lWords)
        if (
            sType == "$mux"
            and bNearest
            and graph.is_variable(dDriver["connections"]["S"][0])
            and (word_value(lWords[0]) is None) != (word_value(lWords[1]) is None)
        ):
            # The multiplexer nearest the register loads a constant: a synchronous reset if its select comes from a
            # top input, see formal.started_machines
            iActive = 1 if word_value(lWords[1]) is not None else 0
            oMachine.reset_select = (sDriver, iActive, word_value(lWords[iActive]))
        for lNext in lWords:
            lWork.append((lNext, sDriver, bNearest and sType in FOLLOWED_TYPES and not bLoads))
    sType = dCell.get("type")
    if sType in ("$adff", "$adffe"):
        oMachine.reset = slice_value(graph.parameter(dCell, "ARST_VALUE", 0), lIndexes)
        oMachine.asynchronous = True
    elif sType in ("$sdff", "$sdffe", "$sdffce"):
        oMachine.reset_select = (sCell, graph.parameter(dCell, "SRST_POLARITY", 1), slice_value(graph.parameter(dCell, "SRST_VALUE", 0), lIndexes))
    if oMachine.reset is not None:
        oMachine.states.setdefault(oMachine.reset, [])
    return oMachine


def slice_value(iValue, lIndexes):
    """The value of bits of a register value, by index, the first the least significant."""
    return sum(((iValue >> i) & 1) << k for k, i in enumerate(lIndexes))


def register_name(dModule, lQ):
    """The name of the signal of a register: the netname whose bits are its output, a named one first."""
    lNames = sorted((s.startswith("$"), s) for s, d in dModule.get("netnames", {}).items() if d.get("bits") == lQ)
    return lNames[0][1].lstrip("\\") if lNames else None


reType = re.compile(r"\btype\s+(\w+)\s+is\s*\(([^;]*?)\)\s*;", re.IGNORECASE | re.DOTALL)
reRecord = re.compile(r"\btype\s+(\w+)\s+is\s+record\b(.*?)\bend\s+record\b", re.IGNORECASE | re.DOTALL)
reField = re.compile(r"([\w\s,]+?)\s*:\s*(\w+)\s*(?:;|$)")
reComment = re.compile(r"--[^\n]*")


def fits(oMachine, lValues):
    """Whether the states of a machine can be the values of an enumerated type, numbered in order by GHDL in as few bits as hold them."""
    return bool(lValues) and max(oMachine.states) < len(lValues) and len(oMachine.bits) == max(1, math.ceil(math.log2(len(lValues))))


def vhdl_names(oMachine, lFiles, sSignalFile=None):
    """
    Sets the names of the states of a state machine from the enumerated type of its signal in the VHDL files, whose
    values GHDL numbers in order from 0. The file of the signal is searched first for its declaration. For a slice of
    a signal of a record type, the field of an enumerated type that fits the slice, if only one does, names the
    machine too.
    """
    sSignal = oMachine.signal.split(".")[-1].split("[")[0].lower()
    reSignal = re.compile(r"\bsignal\s+[\w\s,]*\b" + re.escape(sSignal) + r"\b[\w\s,]*:\s*(\w+)", re.IGNORECASE)
    dTypes = {}
    dRecords = {}
    sType = None
    lOrdered = ([sSignalFile] if sSignalFile else []) + [s for s in lFiles if s != sSignalFile]
    for sFile in lOrdered:
        if not sFile or not os.path.isfile(sFile) or not sFile.lower().endswith((".vhd", ".vhdl")):
            continue
        try:
            with open(sFile, encoding="utf-8", errors="replace") as oFile:
                sText = reComment.sub("", oFile.read())
        except OSError:
            continue
        for oMatch in reType.finditer(sText):
            dTypes.setdefault(oMatch.group(1).lower(), [s.strip() for s in oMatch.group(2).split(",")])
        for oMatch in reRecord.finditer(sText):
            lFields = []
            for oField in reField.finditer(oMatch.group(2)):
                lFields += [(s.strip(), oField.group(2).lower()) for s in oField.group(1).split(",") if s.strip()]
            dRecords.setdefault(oMatch.group(1).lower(), lFields)
        if sType is None:
            oMatch = reSignal.search(sText)
            if oMatch is not None:
                sType = oMatch.group(1).lower()
    if sType is None:
        return
    if sType in dTypes:
        if fits(oMachine, dTypes[sType]):
            oMachine.names = {iValue: dTypes[sType][iValue] for iValue in oMachine.states}
        return
    lFields = [(sField, dTypes[sFieldType]) for sField, sFieldType in dRecords.get(sType, []) if sFieldType in dTypes and fits(oMachine, dTypes[sFieldType])]
    if len(lFields) == 1:
        sField, lValues = lFields[0]
        oMachine.name = f"{oMachine.signal}.{sField}"
        oMachine.names = {iValue: lValues[iValue] for iValue in oMachine.states}


reSvEnum = re.compile(r"\benum\b[^{;]*\{([^}]*)\}\s*(\w+)", re.DOTALL)
reSvComment = re.compile(r"//[^\n]*|/\*.*?\*/", re.DOTALL)
reSvLiteral = re.compile(r"^(?:\d*\s*)?'\s*([sS]?)([bBoOdDhH])\s*([0-9a-fA-F_xXzZ?]+)$")


def sv_value(sText):
    """The value of a SystemVerilog integer literal, such as 3, 2'd3 or 'h1f, or None."""
    sText = sText.strip().replace("_", "")
    if sText.isdigit():
        return int(sText)
    oMatch = reSvLiteral.match(sText)
    if oMatch is None:
        return None
    try:
        return int(oMatch.group(3), {"b": 2, "o": 8, "d": 10, "h": 16}[oMatch.group(2).lower()])
    except ValueError:
        return None


def sv_names(oMachine, lFiles, sSignalFile=None):
    """
    Sets the names of the states of a state machine from the enumeration of its signal in SystemVerilog files: an enum
    typedef whose name declares the signal, or an enum that declares it. Values without one follow the one before.
    """
    sSignal = oMachine.signal.split(".")[-1].split("[")[0]
    lOrdered = ([sSignalFile] if sSignalFile else []) + [s for s in lFiles if s != sSignalFile]
    dTypes = {}
    for sFile in lOrdered:
        if not sFile or not os.path.isfile(sFile) or not sFile.lower().endswith((".sv", ".v", ".svh", ".vh")):
            continue
        try:
            with open(sFile, encoding="utf-8", errors="replace") as oFile:
                sText = reSvComment.sub("", oFile.read())
        except OSError:
            continue
        for oMatch in reSvEnum.finditer(sText):
            dNames = {}
            iNext = 0
            for sMember in oMatch.group(1).split(","):
                sName, _, sValue = sMember.partition("=")
                sName = sName.strip()
                if not sName:
                    continue
                if sValue.strip():
                    iNext = sv_value(sValue)
                    if iNext is None:
                        dNames = {}
                        break
                dNames[iNext] = sName
                iNext += 1
            if dNames:
                dTypes.setdefault(oMatch.group(2), dNames)
        # The signal declared with a typedef name, or by an enum itself
        for sType, dNames in dTypes.items():
            if sType == sSignal or re.search(r"\b" + re.escape(sType) + r"\s+(?:\w+\s*,\s*)*" + re.escape(sSignal) + r"\b", sText):
                if all(i in dNames for i in oMachine.states):
                    oMachine.names = {i: dNames[i] for i in oMachine.states}
                    return


def attribute_names(oMachine, dModule):
    """Sets the names of the states from the enum_value_<bits> attributes of the netname of the register."""
    for dNet in dModule.get("netnames", {}).values():
        if dNet.get("bits") != oMachine.bits:
            continue
        for sKey, oValue in dNet.get("attributes", {}).items():
            if sKey.startswith("enum_value_"):
                iValue = word_value(list(reversed(sKey[len("enum_value_") :])))
                if iValue is not None:
                    oMachine.names[iValue] = str(oValue).lstrip("\\").split("::")[-1]
