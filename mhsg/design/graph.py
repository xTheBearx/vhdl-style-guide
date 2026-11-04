# -*- coding: utf-8 -*-
"""
Bit level graphs of the modules of a Yosys netlist, for the design rules.

Each module is analyzed on its own, before flattening, so findings point at the module that holds the logic. Paths
through instances of other modules use a summary of each module, computed bottom up: which of its inputs reach which
of its outputs without passing a register, which inputs it uses, and the logic depths into and out of it.

A bit is a net bit number of the netlist. Constant bits, "0", "1", "x" and "z", are left out of the graphs.
"""

import copy as copy_module
import fnmatch

from mhsg.design import netlist

# Cells that hold state: their outputs do not depend on their inputs in the same clock cycle
STATE_TYPES = netlist.FLIP_FLOP_TYPES | netlist.LATCH_TYPES | {"$dffsr", "$dffsre", "$aldff", "$aldffe", "$sr", "$ff"}
# Cells with no outputs, or whose effect is outside the logic
SINK_TYPES = {"$memwr", "$memwr_v2", "$meminit", "$meminit_v2", "$mem", "$mem_v2", "$assert", "$assume", "$cover", "$live", "$fair", "$print", "$check"}
# The cells of assertions, assumptions and cover statements
FORMAL_TYPES = {"$assert", "$assume", "$cover", "$live", "$fair", "$check"}
# Cells whose output bit depends on the same bit of the inputs
BITWISE_TYPES = {"$and", "$or", "$xor", "$xnor", "$not", "$pos", "$buf", "$bweqx"}
# Cells that cost no logic level: inverters and buffers
FREE_TYPES = {"$not", "$pos", "$buf"}
# Associative cells: a chain of them is one wide gate, one logic level
ASSOCIATIVE_TYPES = {"$and", "$or", "$xor", "$xnor", "$reduce_and", "$reduce_or", "$reduce_xor", "$reduce_bool", "$logic_and", "$logic_or"}
ARITHMETIC_TYPES = {"$add", "$sub", "$neg"}

NO_DEPTH = -1

# The output ports of the internal cells of Yosys, for cells written without port directions
# Cells that can release their output, besides the multiplexers with a 'z' input GHDL builds, see is_tristate
TRISTATE_TYPES = {"$tribuf", "$_TBUF_"}

OUTPUT_PORTS = {"Y", "Q", "DATA", "RD_DATA", "X", "CO"}


def parameter(dCell, sName, iDefault=0):
    """Returns an integer cell parameter; Yosys writes them as binary strings."""
    oValue = dCell.get("parameters", {}).get(sName)
    if oValue is None:
        return iDefault
    if isinstance(oValue, int):
        return oValue
    try:
        return int(str(oValue), 2)
    except ValueError:
        return iDefault


def is_state(dCell):
    sType = dCell.get("type", "")
    if sType in STATE_TYPES:
        return True
    # A memory read port with a clock is a register
    return sType in ("$memrd", "$memrd_v2") and parameter(dCell, "CLK_ENABLE") != 0


def is_tristate(dCell):
    """Returns whether a cell can release its output: a tri-state buffer, or a multiplexer with a 'z' input, as GHDL builds them."""
    if dCell.get("type") in TRISTATE_TYPES:
        return True
    if dCell.get("type") in ("$mux", "$pmux"):
        dConnections = dCell.get("connections", {})
        return "z" in dConnections.get("A", []) + dConnections.get("B", [])
    return False


def is_variable(oBit):
    return isinstance(oBit, int)


def extend(lBits, iIndex, bSigned):
    """Returns the bit of an operand at an index of the result, extended with its sign or zeros."""
    if iIndex < len(lBits):
        return lBits[iIndex]
    if bSigned and lBits:
        return lBits[-1]
    return None


class Summary:
    """What a module looks like from an instance of it."""

    def __init__(self):
        # (output port, index) -> set of (input port, index) it depends on without a register in between
        self.through = {}
        # (input port, index) of the inputs the module uses
        self.used_inputs = set()
        # (output port, index) -> logic depth from a register or memory in the module, or NO_DEPTH
        self.launch = {}
        # (output port, index) -> logic depth from any input of the module, or NO_DEPTH
        self.pass_depth = {}
        # (input port, index) -> logic depth from the input to a register or memory in the module, or NO_DEPTH
        self.capture = {}
        # (output port, index) of the outputs only tri-state drivers drive
        self.tristate = set()


class ModuleGraph:
    """The bit graph of one module."""

    def __init__(self, oDesign, sModule):
        self.design = oDesign
        self.name = sModule
        self.module = oDesign.netlist.modules[sModule]
        self.cells = self.module.get("cells", {})
        self.ports = self.module.get("ports", {})
        self.latch_cells = oDesign.latch_cells.get(sModule, set())
        # bit -> list of (cell name, port, index); module inputs are (None, port, index)
        self.drivers = {}
        # bit -> list of (cell name, port, index); module outputs are (None, port, index)
        self.readers = {}
        for sPort, dPort in self.ports.items():
            for iIndex, oBit in enumerate(dPort.get("bits", [])):
                if not is_variable(oBit):
                    continue
                if dPort.get("direction") in ("input", "inout"):
                    self.drivers.setdefault(oBit, []).append((None, sPort, iIndex))
                if dPort.get("direction") in ("output", "inout"):
                    self.readers.setdefault(oBit, []).append((None, sPort, iIndex))
        for sCell, dCell in self.cells.items():
            for sPort, lBits in dCell.get("connections", {}).items():
                sDirection = self.direction(dCell, sPort)
                for iIndex, oBit in enumerate(lBits):
                    if not is_variable(oBit):
                        continue
                    if sDirection in ("output", "inout"):
                        self.drivers.setdefault(oBit, []).append((sCell, sPort, iIndex))
                    if sDirection in ("input", "inout"):
                        self.readers.setdefault(oBit, []).append((sCell, sPort, iIndex))
        self._dInputs = None
        self._lComponents = None
        self._dPredecessors = None
        self._dSuccessors = None
        self._dStart = None

    # Cells

    def direction(self, dCell, sPort):
        sDirection = dCell.get("port_directions", {}).get(sPort)
        if sDirection is None:
            dPorts = self.design.module_ports(dCell.get("type"))
            if dPorts is not None:
                sDirection = dPorts.get(sPort, "input")
            else:
                sDirection = "output" if sPort in OUTPUT_PORTS else "input"
        return sDirection

    def is_state(self, sCell):
        return sCell in self.latch_cells or is_state(self.cells[sCell])

    def is_instance(self, sCell):
        return not self.cells[sCell].get("type", "$").startswith("$")

    def drives_tristate(self, sCell, sPort, iIndex):
        """Returns whether an output bit of a cell is a tri-state driver: a tri-state cell, or a tri-state output of an instance."""
        dCell = self.cells[sCell]
        if is_tristate(dCell):
            return True
        if self.is_instance(sCell):
            oChild = self.child(sCell)
            return oChild is not None and (sPort, iIndex) in oChild.tristate
        return False

    def child(self, sCell):
        """Returns the summary of the module an instance cell instantiates, or None for a black box."""
        return self.design.summary(self.cells[sCell].get("type"))

    def box_path(self, sCell, sPort):
        """
        Returns the path role declared for an output port of a black box, see black_box.py, or None. The declarations
        of the type apply, and those of single instances when they apply to every instance of the cell in the design.
        """
        return self.design.box_role(self.cells[sCell], sPort, "path", self.name, sCell)

    def input_bits(self, sCell):
        dCell = self.cells[sCell]
        return [
            b for sPort, lBits in dCell.get("connections", {}).items() if self.direction(dCell, sPort) in ("input", "inout") for b in lBits if is_variable(b)
        ]

    def output_bits(self, sCell):
        """Returns (port, index, bit) for each variable output bit of a cell."""
        dCell = self.cells[sCell]
        return [
            (sPort, iIndex, oBit)
            for sPort, lBits in dCell.get("connections", {}).items()
            if self.direction(dCell, sPort) in ("output", "inout")
            for iIndex, oBit in enumerate(lBits)
            if is_variable(oBit)
        ]

    def comb_inputs(self, sCell, sPort, iIndex):
        """Returns the bits an output bit of a cell depends on without a register in between."""
        dCell = self.cells[sCell]
        if self.is_state(sCell) or dCell.get("type") in SINK_TYPES:
            return []
        if self.is_instance(sCell):
            oChild = self.child(sCell)
            if oChild is None:
                # A black box: its outputs are registered unless a declared path leads through it
                oRole = self.box_path(sCell, sPort)
                return box_path_bits(dCell.get("connections", {}), oRole, iIndex) if oRole is not None else []
            dConnections = dCell.get("connections", {})
            lReturn = []
            for sInput, iInput in oChild.through.get((sPort, iIndex), ()):
                lBits = dConnections.get(sInput, [])
                if iInput < len(lBits) and is_variable(lBits[iInput]):
                    lReturn.append(lBits[iInput])
            return lReturn
        sType = dCell.get("type")
        dConnections = dCell.get("connections", {})
        lA = dConnections.get("A", [])
        lB = dConnections.get("B", [])
        if sType in BITWISE_TYPES:
            lReturn = [extend(lA, iIndex, parameter(dCell, "A_SIGNED")), extend(lB, iIndex, parameter(dCell, "B_SIGNED"))]
        elif sType == "$mux":
            lReturn = [extend(lA, iIndex, False), extend(lB, iIndex, False)] + dConnections.get("S", [])
        elif sType == "$pmux":
            iWidth = parameter(dCell, "WIDTH", len(lA)) or 1
            lReturn = [extend(lA, iIndex, False)] + lB[iIndex::iWidth] + dConnections.get("S", [])
        elif sType == "$bwmux":
            lReturn = [extend(lA, iIndex, False), extend(lB, iIndex, False), extend(dConnections.get("S", []), iIndex, False)]
        elif sType in ARITHMETIC_TYPES:
            # A carry only moves towards the most significant bit
            lReturn = lA[: iIndex + 1] + lB[: iIndex + 1]
            if iIndex >= len(lA) and parameter(dCell, "A_SIGNED"):
                lReturn += lA[-1:]
            if iIndex >= len(lB) and parameter(dCell, "B_SIGNED"):
                lReturn += lB[-1:]
        elif sType == "$tribuf":
            lReturn = [extend(lA, iIndex, False)] + dConnections.get("EN", [])
        else:
            lReturn = self.input_bits(sCell)
        return [b for b in lReturn if is_variable(b)]

    # The combinational graph

    def edges(self):
        """
        Builds the combinational edges once: for each bit, the bits it depends on with the logic levels in between,
        and the depth at which a path starts at the bit, if it is driven by a register, memory, black box or constant logic.
        """
        if self._dPredecessors is not None:
            return
        self._dPredecessors = {}
        self._dSuccessors = {}
        self._dStart = {}
        for sCell, dCell in self.cells.items():
            bState = self.is_state(sCell) or dCell.get("type") in SINK_TYPES
            oChild = self.child(sCell) if self.is_instance(sCell) else None
            for sPort, iIndex, iBit in self.output_bits(sCell):
                bBox = self.is_instance(sCell) and oChild is None
                if bState or (bBox and self.box_path(sCell, sPort) is None):
                    self._dStart[iBit] = max(self._dStart.get(iBit, NO_DEPTH), 0)
                    continue
                lInputs = self.comb_inputs(sCell, sPort, iIndex)
                if bBox:
                    # A declared path through a black box, such as a buffer, adds no logic level that can be seen
                    if not lInputs:
                        self._dStart[iBit] = max(self._dStart.get(iBit, NO_DEPTH), 0)
                    lEdges = [(iInput, 0) for iInput in lInputs]
                elif oChild is not None:
                    self._dStart[iBit] = max(self._dStart.get(iBit, NO_DEPTH), oChild.launch.get((sPort, iIndex), NO_DEPTH))
                    lEdges = [(iInput, max(oChild.pass_depth.get((sPort, iIndex), 0), 0)) for iInput in lInputs]
                else:
                    if not lInputs:
                        self._dStart[iBit] = max(self._dStart.get(iBit, NO_DEPTH), 0)
                    lEdges = [(iInput, self.weight(sCell, iInput)) for iInput in lInputs]
                self._dPredecessors.setdefault(iBit, []).extend(lEdges)
                for iInput, iWeight in lEdges:
                    self._dSuccessors.setdefault(iInput, []).append((iBit, iWeight))

    def comb_drivers(self, iBit):
        """Returns the bits that drive a bit through one cell, without a register in between."""
        self.edges()
        return [iDriver for iDriver, _ in self._dPredecessors.get(iBit, [])]

    def driving_cell(self, iBit):
        """Returns the name of the first cell that drives a bit, or None for a module input or an undriven bit."""
        for sCell, _, _ in self.drivers.get(iBit, []):
            if sCell is not None:
                return sCell
        return None

    def all_bits(self):
        return set(self.drivers) | set(self.readers)

    def components(self):
        """
        Returns the strongly connected components of the combinational graph, sources first, each a list of bits.
        A component of more than one bit, or a bit that drives itself, is a combinational loop.
        """
        if self._lComponents is None:
            self._lComponents = strongly_connected(sorted(self.all_bits()), self.comb_drivers)
        return self._lComponents

    def loops(self):
        """Returns the combinational loops, each a list of bits."""
        lReturn = []
        for lComponent in self.components():
            if len(lComponent) > 1 or lComponent[0] in self.comb_drivers(lComponent[0]):
                lReturn.append(lComponent)
        return lReturn

    # Summaries

    def input_index(self):
        """Returns {bit: [(input port, index)]} for the input bits of the module."""
        if self._dInputs is None:
            self._dInputs = {}
            for sPort, dPort in self.ports.items():
                if dPort.get("direction") in ("input", "inout"):
                    for iIndex, oBit in enumerate(dPort.get("bits", [])):
                        if is_variable(oBit):
                            self._dInputs.setdefault(oBit, []).append((sPort, iIndex))
        return self._dInputs

    def summarize(self):
        oSummary = Summary()
        dInputs = self.input_index()
        # Which inputs reach each bit without a register, in topological order
        dReach = {}
        for lComponent in self.components():
            setReach = set()
            setComponent = set(lComponent)
            for iBit in lComponent:
                setReach.update(dInputs.get(iBit, []))
                for iDriver in self.comb_drivers(iBit):
                    if iDriver not in setComponent:
                        setReach |= dReach.get(iDriver, set())
            for iBit in lComponent:
                dReach[iBit] = setReach
        dDepth = self.depths()
        for sPort, dPort in self.ports.items():
            if dPort.get("direction") not in ("output", "inout"):
                continue
            for iIndex, oBit in enumerate(dPort.get("bits", [])):
                if not is_variable(oBit):
                    continue
                if dPort.get("direction") == "inout":
                    # The bit of an inout port is its input too, which does not drive the output side: only what the
                    # drivers inside reach does, else every instance with an inout port would be a loop in its parent
                    setThrough = set()
                    for iDriver in self.comb_drivers(oBit):
                        setThrough |= dReach.get(iDriver, set())
                    oSummary.through[(sPort, iIndex)] = setThrough
                else:
                    oSummary.through[(sPort, iIndex)] = dReach.get(oBit, set())
                iLaunch, iPass = dDepth.get(oBit, (NO_DEPTH, NO_DEPTH))
                lDrivers = [t for t in self.drivers.get(oBit, []) if t[0] is not None]
                if lDrivers and all(self.drives_tristate(*t) for t in lDrivers):
                    oSummary.tristate.add((sPort, iIndex))
                oSummary.launch[(sPort, iIndex)] = iLaunch
                oSummary.pass_depth[(sPort, iIndex)] = iPass
        setLive = self.live_bits()
        dRequired = self.required_depths()
        for iBit, lInputs in dInputs.items():
            for tInput in lInputs:
                if iBit in setLive:
                    oSummary.used_inputs.add(tInput)
                oSummary.capture[tInput] = dRequired.get(iBit, NO_DEPTH)
        return oSummary

    # Logic depth

    def weight(self, sCell, iDriver):
        """Returns the logic levels a cell adds to a path that enters it from a bit."""
        sType = self.cells[sCell].get("type")
        if sType in FREE_TYPES:
            return 0
        if sType in ASSOCIATIVE_TYPES:
            sDriver = self.driving_cell(iDriver)
            if sDriver is not None and self.cells[sDriver].get("type") == sType:
                return 0
        return 1

    def depths(self):
        """
        Returns {bit: (depth from a register or memory, depth from a module input)}, in logic levels, NO_DEPTH where there is no such path.
        Paths through instances add the depths of the instantiated module.
        """
        self.edges()
        dReturn = {}
        setInputs = set(self.input_index())
        for lComponent in self.components():
            for iBit in lComponent:
                iLaunch = self._dStart.get(iBit, NO_DEPTH)
                if not self.drivers.get(iBit):
                    iLaunch = max(iLaunch, 0)
                iPass = 0 if iBit in setInputs else NO_DEPTH
                for iDriver, iWeight in self._dPredecessors.get(iBit, []):
                    iDriverLaunch, iDriverPass = dReturn.get(iDriver, (NO_DEPTH, NO_DEPTH))
                    if iDriverLaunch != NO_DEPTH:
                        iLaunch = max(iLaunch, iDriverLaunch + iWeight)
                    if iDriverPass != NO_DEPTH:
                        iPass = max(iPass, iDriverPass + iWeight)
                dReturn[iBit] = (iLaunch, iPass)
        return dReturn

    def endpoints(self):
        """
        Yields (cell, bit, extra depth) for each bit that ends a path in the module: an input of a register, a memory or
        a black box, or an input of an instance, with the depth the path continues inside it.
        """
        for sCell, dCell in self.cells.items():
            if self.is_instance(sCell):
                oChild = self.child(sCell)
                for sPort, lBits in dCell.get("connections", {}).items():
                    if self.direction(dCell, sPort) not in ("input", "inout"):
                        continue
                    for iIndex, oBit in enumerate(lBits):
                        if not is_variable(oBit):
                            continue
                        iCapture = 0 if oChild is None else oChild.capture.get((sPort, iIndex), NO_DEPTH)
                        if iCapture != NO_DEPTH:
                            yield sCell, oBit, iCapture
            elif self.is_state(sCell) or dCell.get("type") in SINK_TYPES:
                for sPort, lBits in dCell.get("connections", {}).items():
                    if sPort in ("CLK", "C") or self.direction(dCell, sPort) not in ("input", "inout"):
                        continue
                    for oBit in lBits:
                        if is_variable(oBit):
                            yield sCell, oBit, 0

    def required_depths(self):
        """Returns {bit: the logic depth from the bit to the end of the longest path in the module}, NO_DEPTH where there is none."""
        self.edges()
        dReturn = {}
        for _, iBit, iExtra in self.endpoints():
            dReturn[iBit] = max(dReturn.get(iBit, NO_DEPTH), iExtra)
        for lComponent in reversed(self.components()):
            for iBit in lComponent:
                iRequired = dReturn.get(iBit, NO_DEPTH)
                for iNext, iWeight in self._dSuccessors.get(iBit, []):
                    if dReturn.get(iNext, NO_DEPTH) != NO_DEPTH:
                        iRequired = max(iRequired, dReturn[iNext] + iWeight)
                dReturn[iBit] = iRequired
        return dReturn

    # Liveness

    def live_bits(self):
        """
        Returns the bits whose value matters: those that reach an output of the module, an input a black box or an
        instance uses, a memory that is read, or an assertion.
        """
        lWork = []
        for sPort, dPort in self.ports.items():
            if dPort.get("direction") in ("output", "inout"):
                lWork.extend(b for b in dPort.get("bits", []) if is_variable(b))
        dMemoryWrites = {}
        for sCell, dCell in self.cells.items():
            sType = dCell.get("type")
            if sType in ("$memwr", "$memwr_v2", "$meminit", "$meminit_v2"):
                dMemoryWrites.setdefault(dCell.get("parameters", {}).get("MEMID"), []).append(sCell)
            elif sType in SINK_TYPES:
                lWork.extend(self.input_bits(sCell))
            elif self.is_instance(sCell):
                oChild = self.child(sCell)
                for sPort, lBits in dCell.get("connections", {}).items():
                    if self.direction(dCell, sPort) not in ("input", "inout"):
                        continue
                    for iIndex, oBit in enumerate(lBits):
                        if is_variable(oBit) and (oChild is None or (sPort, iIndex) in oChild.used_inputs):
                            lWork.append(oBit)
        setLive = set()
        setCells = set()
        while lWork:
            iBit = lWork.pop()
            if iBit in setLive:
                continue
            setLive.add(iBit)
            for sCell, _, _ in self.drivers.get(iBit, []):
                if sCell is None or sCell in setCells:
                    continue
                setCells.add(sCell)
                dCell = self.cells[sCell]
                if self.is_instance(sCell):
                    # The outputs of an instance are live; its inputs were added if the instance uses them
                    continue
                lWork.extend(self.input_bits(sCell))
                if dCell.get("type") in ("$memrd", "$memrd_v2"):
                    for sWrite in dMemoryWrites.pop(dCell.get("parameters", {}).get("MEMID"), []):
                        lWork.extend(self.input_bits(sWrite))
        return setLive

    # Registers

    def registers(self):
        """Yields the names of the flip-flop cells of the module, leaving out those of assertions."""
        for sCell, dCell in self.cells.items():
            if dCell.get("type") in netlist.FLIP_FLOP_TYPES and not self.assertion_register(sCell):
                yield sCell

    def assertion_register(self, sCell):
        """
        Returns whether a flip-flop only feeds assertions. GHDL makes one for each assert of a clocked process, to hold
        its condition until the clock edge; it checks the design and is not part of it.
        """
        lReaders = [t for oBit in self.cells[sCell].get("connections", {}).get("Q", []) if is_variable(oBit) for t in self.readers.get(oBit, [])]
        return bool(lReaders) and all(sReader is not None and self.cells[sReader].get("type") in FORMAL_TYPES for sReader, _, _ in lReaders)

    def register_value(self, sCell, iIndex):
        """
        Returns the only value a bit of a register can ever have, "0" or "1", "" if it is never assigned and has no
        reset, or None if it can change. The data input is followed back through multiplexers, ignoring the paths
        that keep the value, such as a clock enable; a bit is constant if all others are the same constant.
        """
        dCell = self.cells[sCell]
        dConnections = dCell.get("connections", {})
        lQ = dConnections.get("Q", [])
        lD = dConnections.get("D", [])
        if iIndex >= len(lQ) or iIndex >= len(lD):
            return None
        setValues = set()
        for sReset in ("ARST_VALUE", "SRST_VALUE"):
            sValue = str(dCell.get("parameters", {}).get(sReset, ""))
            if sValue and iIndex < len(sValue):
                setValues.add(sValue[-1 - iIndex])
        if dCell.get("type") in ("$dffsr", "$dffsre", "$aldff", "$aldffe"):
            return None
        lWork = [lD[iIndex]]
        setSeen = set()
        while lWork:
            oBit = lWork.pop()
            if not is_variable(oBit):
                if oBit in ("0", "1"):
                    setValues.add(oBit)
                continue
            if oBit == lQ[iIndex] or oBit in setSeen:
                continue
            setSeen.add(oBit)
            sDriver = self.driving_cell(oBit)
            if sDriver is None:
                return None
            dDriver = self.cells[sDriver]
            sType = dDriver.get("type")
            if sType not in ("$mux", "$pmux", "$pos", "$buf"):
                return None
            lY = dDriver.get("connections", {}).get("Y", [])
            iOut = lY.index(oBit)
            lA = dDriver["connections"].get("A", [])
            lWork.append(extend(lA, iOut, False))
            if sType == "$mux":
                lWork.append(extend(dDriver["connections"].get("B", []), iOut, False))
            elif sType == "$pmux":
                iWidth = parameter(dDriver, "WIDTH", len(lA)) or 1
                lWork.extend(dDriver["connections"].get("B", [])[iOut::iWidth])
            if len(setValues) > 1:
                return None
        if len(setValues) > 1:
            return None
        return setValues.pop() if setValues else ""

    # Names

    def bit_name(self, iBit):
        return self.design.netlist.bit_name(self.name, iBit)

    def net_bits(self, sName):
        dNet = self.module.get("netnames", {}).get(sName, {})
        return [b for b in dNet.get("bits", []) if is_variable(b)]

    def named_nets(self):
        """Yields (name, bits) for the nets named in the VHDL, not the ports."""
        for sName, dNet in self.module.get("netnames", {}).items():
            if dNet.get("hide_name") or sName.startswith("$") or sName in self.ports:
                continue
            yield sName, [b for b in dNet.get("bits", []) if is_variable(b)]


class DesignGraph:
    """The graphs and summaries of all modules of a netlist."""

    def __init__(self, oNetlist, oBlackBoxes=None, fPaths=None):
        self.netlist = oNetlist
        # The black box declarations, see black_box.py
        self.black_boxes = oBlackBoxes
        # (module, cell) -> the flat names of the instances of the cell in the design, such as u_top.u_box
        self.paths = fPaths
        self._dBoxes = {}
        self.latch_cells = {}
        for sModule, sCell, _ in oNetlist.latches():
            self.latch_cells.setdefault(sModule, set()).add(sCell)
        self._dGraphs = {}
        self._dSummaries = {}
        self._lInProgress = []

    def graph(self, sModule):
        if sModule not in self._dGraphs:
            self._dGraphs[sModule] = ModuleGraph(self, sModule)
        return self._dGraphs[sModule]

    def modules(self):
        """Returns the module names, each after the modules it instantiates."""
        lReturn = []
        setDone = set()

        def visit(sModule, lPath):
            if sModule in setDone or sModule in lPath or sModule not in self.netlist.modules:
                return
            for dCell in self.netlist.modules[sModule].get("cells", {}).values():
                visit(dCell.get("type"), lPath + [sModule])
            setDone.add(sModule)
            lReturn.append(sModule)

        for sModule in sorted(self.netlist.modules):
            visit(sModule, [])
        return lReturn

    def summary(self, sModule):
        """Returns the summary of a module, or None if it is not in the netlist, which makes it a black box."""
        if sModule not in self.netlist.modules or sModule in self._lInProgress:
            return None
        if sModule not in self._dSummaries:
            self._lInProgress.append(sModule)
            try:
                self._dSummaries[sModule] = self.graph(sModule).summarize()
            finally:
                self._lInProgress.remove(sModule)
        return self._dSummaries[sModule]

    def box_role(self, dCell, sPort, sKind, sModule=None, sCell=None):
        """
        The role of a kind declared for a port of a black box cell, or None: by the declarations of single instances
        when the same ones apply to every instance of the cell in the design, then by those of its type.
        """
        if self.black_boxes is None:
            return None
        # Imported here: black_box imports this module
        from mhsg.design import black_box  # pylint: disable=import-outside-toplevel

        sType = str(dCell.get("type"))
        lInstances = self.instance_declarations(sModule, sCell)
        tKey = (sType, tuple(sorted((str(k), str(v)) for k, v in (dCell.get("parameters") or {}).items())), tuple(id(o) for o in lInstances))
        if tKey not in self._dBoxes:
            lDeclarations = lInstances + self.black_boxes.find_type(sType)
            self._dBoxes[tKey] = black_box.Instance(CellView(dCell), lDeclarations) if lDeclarations else None
        oInstance = self._dBoxes[tKey]
        oRole = oInstance.role(sPort) if oInstance is not None else None
        return oRole if oRole is not None and oRole.kind == sKind else None

    def instance_declarations(self, sModule, sCell):
        """
        The declarations of single instances that apply to every instance of a cell in the design, which a module graph
        shares; none when they differ between the instances.
        """
        if self.paths is None or sModule is None or not self.black_boxes.instances:
            return []
        lFound = []
        for iPath, sPath in enumerate(self.paths(sModule, sCell)):
            lDeclarations = [o for o in self.black_boxes.instances if fnmatch.fnmatchcase(sPath.lower(), o.name.lower())]
            if iPath > 0 and [id(o) for o in lDeclarations] != [id(o) for o in lFound]:
                return []
            lFound = lDeclarations
        return lFound

    def module_ports(self, sModule):
        """Returns {port: direction} of a module in the netlist, or None."""
        dModule = self.netlist.modules.get(sModule)
        if dModule is None:
            return None
        return {sPort: dPort.get("direction") for sPort, dPort in dModule.get("ports", {}).items()}


class CellView:
    """A cell of a module as black_box.Instance sees a cell of the flat netlist."""

    def __init__(self, dCell):
        self.cell = dCell
        self.type = dCell.get("type")
        self.connections = dCell.get("connections", {})


def box_path_bits(dConnections, oRole, iIndex):
    """The input bits an output bit of a black box follows through a path role."""
    # Imported here: black_box imports this module
    from mhsg.design import black_box  # pylint: disable=import-outside-toplevel

    return black_box.path_bits(dConnections, oRole, iIndex)


def strongly_connected(lNodes, fPredecessors):
    """
    Returns the strongly connected components of a graph given by a function from a node to its predecessors,
    ordered so that each component comes after the components of its predecessors. Iterative Tarjan.
    """
    dIndex = {}
    dLow = {}
    setOnStack = set()
    lStack = []
    lReturn = []
    iCounter = 0
    for oStart in lNodes:
        if oStart in dIndex:
            continue
        lWork = [(oStart, iter(fPredecessors(oStart)))]
        dIndex[oStart] = dLow[oStart] = iCounter
        iCounter += 1
        lStack.append(oStart)
        setOnStack.add(oStart)
        while lWork:
            oNode, oIterator = lWork[-1]
            bPushed = False
            for oNext in oIterator:
                if oNext not in dIndex:
                    dIndex[oNext] = dLow[oNext] = iCounter
                    iCounter += 1
                    lStack.append(oNext)
                    setOnStack.add(oNext)
                    lWork.append((oNext, iter(fPredecessors(oNext))))
                    bPushed = True
                    break
                if oNext in setOnStack:
                    dLow[oNode] = min(dLow[oNode], dIndex[oNext])
            if bPushed:
                continue
            lWork.pop()
            if lWork:
                dLow[lWork[-1][0]] = min(dLow[lWork[-1][0]], dLow[oNode])
            if dLow[oNode] == dIndex[oNode]:
                lComponent = []
                while True:
                    oMember = lStack.pop()
                    setOnStack.discard(oMember)
                    lComponent.append(oMember)
                    if oMember == oNode:
                        break
                lReturn.append(lComponent)
    return lReturn


# The separator between the name of a module and the instance path of a copy of it, see instance_copies
COPY_SEPARATOR = "$mhsg$"


def instance_copies(oNetlist, oBlackBoxes, fPaths):
    """
    Returns (netlist, paths) in which each module whose black boxes have declarations of single instances that differ
    between its instances, and each module above it, has a copy for each instance, named module$mhsg$path, so the
    declarations of each instance apply to its copy; or None when no declaration differs. paths gives the flat names
    of the instances of a black box cell, as fPaths does for the netlist.
    """
    if oBlackBoxes is None or not oBlackBoxes.instances or fPaths is None:
        return None
    setDiffer = set()
    for sModule, dModule in oNetlist.modules.items():
        for sCell, dCell in dModule.get("cells", {}).items():
            if str(dCell.get("type", "")).startswith("$") or dCell.get("type") in oNetlist.modules:
                continue
            lFound = {tuple(id(o) for o in oBlackBoxes.instances if fnmatch.fnmatchcase(s.lower(), o.name.lower())) for s in fPaths(sModule, sCell)}
            if len(lFound) > 1:
                setDiffer.add(sModule)
    if not setDiffer:
        return None
    dNeeds = {}

    def needs(sModule, lStack=()):
        if sModule not in dNeeds:
            dNeeds[sModule] = sModule in setDiffer or any(
                needs(d.get("type"), lStack + (sModule,))
                for d in oNetlist.modules[sModule].get("cells", {}).values()
                if d.get("type") in oNetlist.modules and d.get("type") not in lStack
            )
        return dNeeds[sModule]

    dModules = dict(oNetlist.modules)
    dPrefixes = {}

    def copy(sModule, tPath):
        sName = sModule + COPY_SEPARATOR + ".".join(tPath) if tPath else sModule
        if sName in dPrefixes:
            return sName
        dPrefixes[sName] = tPath
        dModule = dict(oNetlist.modules[sModule])
        dCells = {}
        for sCell, dCell in dModule.get("cells", {}).items():
            sType = dCell.get("type")
            if sType in oNetlist.modules and needs(sType):
                dCell = dict(dCell)
                dCell["type"] = copy(sType, tPath + (sCell.lstrip("\\"),))
            dCells[sCell] = dCell
        dModule["cells"] = dCells
        dModules[sName] = dModule
        return sName

    setInstantiated = {d.get("type") for m in oNetlist.modules.values() for d in m.get("cells", {}).values()}
    for sModule in list(oNetlist.modules):
        if sModule not in setInstantiated and needs(sModule):
            copy(sModule, ())
    # The originals that only copies stand for are left out, so they are not checked with no declaration
    for sModule in setInstantiated:
        if sModule in dModules and needs(sModule) and sModule not in dPrefixes:
            del dModules[sModule]
    oCopy = copy_module.copy(oNetlist)
    oCopy.modules = dModules

    def paths(sModule, sCell):
        if COPY_SEPARATOR in sModule:
            return [".".join(dPrefixes[sModule] + (sCell,))]
        return fPaths(sModule, sCell)

    return oCopy, paths
