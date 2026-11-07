# -*- coding: utf-8 -*-
"""
The design in test mode, for the design for test rules design_039 to design_042.

The design section names the top inputs that select test mode and their values there, under test_mode, and those that
select the shift of the scan chains, under scan_shift:

    design:
      test_mode:
        scan_mode: 1
      scan_shift:
        scan_enable: 1

Their values are propagated through the logic of the flat design: a net whose value follows from them is constant in
test mode. The clock of each register and latch is then followed back from its pin, through buffers, inverters, gates
and multiplexers whose other inputs are constant, to the top input or clock output of a black box it comes from. Where
it cannot be followed, the clock is not controlled by the tester: it comes from a register or a latch, passes a gate
or a multiplexer whose other inputs change, or is held constant.
"""

from mhsg import exceptions
from mhsg.design import cdc, graph, netlist

INVERTERS = {"$not", "$_NOT_", "$logic_not"}
BUFFERS = {"$pos", "$buf", "$_BUF_"}
AND_TYPES = {"$and", "$_AND_", "$logic_and", "$reduce_and"}
OR_TYPES = {"$or", "$_OR_", "$logic_or", "$reduce_or", "$reduce_bool"}
MUX_TYPES = {"$mux", "$_MUX_"}

# What stops the clock of a register from being followed back to a source the tester controls
FROM_REGISTER = "register"
FROM_LATCH = "latch"
FROM_BOX = "black box"
GATED = "gate"
MULTIPLEXER = "multiplexer"
CONSTANT = "constant"
UNKNOWN = "logic"


def read_values(oValue, sKey):
    """{top input: 0 or 1} of the test_mode or scan_shift key of the design section."""
    if oValue is None:
        return {}
    if not isinstance(oValue, dict):
        raise exceptions.ConfigurationError(f"ERROR: {sKey} in the design section maps top inputs to their values, such as scan_mode: 1")
    dReturn = {}
    for sPort, oSetting in oValue.items():
        if isinstance(oSetting, bool):
            oSetting = int(oSetting)
        if oSetting not in (0, 1, "0", "1"):
            raise exceptions.ConfigurationError(f"ERROR: {sKey} in the design section: the value of {sPort} is {oSetting}; expected 0 or 1")
        dReturn[str(sPort)] = int(oSetting)
    return dReturn


class Source:
    """Where the clock of a register or latch comes from in test mode."""

    def __init__(self, sName=None, iInverted=0, sProblem=None, oCell=None, sDetail=""):
        # The top input or black box output the clock comes from, when it is controlled
        self.name = sName
        # 1 when the clock is inverted on its way
        self.inverted = iInverted
        # Why the clock is not controlled, see FROM_REGISTER and the others; None when it is
        self.problem = sProblem
        # The cell where the clock stops being controlled, and what about it
        self.cell = oCell
        self.detail = sDetail


class TestMode:
    """The constant nets of the flat design in test mode, and the sources of its clocks."""

    def __init__(self, oAnalysis, dValues):
        self.analysis = oAnalysis
        self.flat = oAnalysis.flat
        self.values = dict(dValues)
        self._dPorts = {}
        for sPort, (_, lNets) in self.flat.top_ports.items():
            for iIndex, oNet in enumerate(lNets):
                self._dPorts[oNet] = (sPort, iIndex, len(lNets))
        self._dValue = {}
        self._dSource = {}

    # Values

    def port_value(self, oNet):
        tPort = self._dPorts.get(oNet)
        if tPort is None:
            return None
        sPort, iIndex, iWidth = tPort
        for sName, iValue in self.values.items():
            if sName.lower() == sPort.lower() and iWidth == 1:
                return iValue
            if sName.lower() == f"{sPort}({iIndex})".lower() or sName.lower() == f"{sPort}[{iIndex}]".lower():
                return iValue
        return None

    def value(self, oNet, iDepth=0):
        """0 or 1 when a net is constant in test mode, else None."""
        if oNet in ("0", "1"):
            return int(oNet)
        if not graph.is_variable(oNet):
            return None
        if oNet in self._dValue:
            return self._dValue[oNet]
        if iDepth > 500:
            return None
        self._dValue[oNet] = None
        iValue = self.port_value(oNet)
        if iValue is None:
            tDriver = self.flat.driver(oNet)
            if tDriver is not None and tDriver[0] is not None:
                iValue = self.cell_value(tDriver[0], tDriver[1], tDriver[2], iDepth + 1)
        self._dValue[oNet] = iValue
        return iValue

    def cell_value(self, oCell, sPort, iIndex, iDepth):
        """The value of an output bit of a cell from the values of its inputs, or None."""
        sType = oCell.type
        if oCell.is_black_box():
            oRole = self.analysis.box_role(oCell, sPort)
            if oRole is not None and oRole.kind == "path":
                lInputs = self.analysis.path_inputs(oCell, oRole, iIndex)
                return self.value(lInputs[0], iDepth) if len(lInputs) == 1 else None
            return None
        if sType in netlist.LATCH_TYPES:
            return self.latch_value(oCell, iIndex, iDepth)
        if sType in graph.STATE_TYPES or not sType.startswith("$"):
            return None
        lA = oCell.connections.get("A", [])
        lB = oCell.connections.get("B", [])
        bSigned = bool(oCell.parameter("A_SIGNED"))
        if sType in BUFFERS:
            return self.value(graph.extend(lA, iIndex, bSigned), iDepth)
        if sType in ("$not", "$_NOT_"):
            iA = self.value(graph.extend(lA, iIndex, bSigned), iDepth)
            return None if iA is None else 1 - iA
        if sType in MUX_TYPES:
            iSelect = self.value(oCell.connections.get("S", [None])[0], iDepth)
            oA = graph.extend(lA, iIndex, False)
            oB = graph.extend(lB, iIndex, False)
            # An input that is x, a value synthesis may choose, takes the value of the other
            if oA == "x":
                oA = oB
            if oB == "x":
                oB = oA
            if iSelect is None:
                iA = self.value(oA, iDepth)
                iB = self.value(oB, iDepth)
                return iA if iA is not None and iA == iB else None
            return self.value(oB if iSelect else oA, iDepth)
        if sType in ("$and", "$_AND_", "$or", "$_OR_", "$xor", "$_XOR_", "$xnor", "$_XNOR_", "$_NAND_", "$_NOR_", "$_ANDNOT_", "$_ORNOT_"):
            iA = self.value(graph.extend(lA, iIndex, bSigned), iDepth)
            iB = self.value(graph.extend(lB, iIndex, bool(oCell.parameter("B_SIGNED"))), iDepth)
            return gate(sType, iA, iB)
        if iIndex > 0 and sType in ("$logic_not", "$logic_and", "$logic_or", "$reduce_and", "$reduce_or", "$reduce_bool", "$reduce_xor", "$eq", "$ne"):
            return 0
        if sType in ("$reduce_and", "$logic_and"):
            return all_of(self.reduce(lA, iDepth) + (self.reduce(lB, iDepth) if sType == "$logic_and" else []), 1)
        if sType in ("$reduce_or", "$reduce_bool", "$logic_or"):
            return any_of(self.reduce(lA, iDepth) + (self.reduce(lB, iDepth) if sType == "$logic_or" else []))
        if sType == "$logic_not":
            iA = any_of(self.reduce(lA, iDepth))
            return None if iA is None else 1 - iA
        if sType in ("$eq", "$ne"):
            iWidth = max(len(lA), len(lB))
            lPairs = [(self.value(graph.extend(lA, i, bSigned), iDepth), self.value(graph.extend(lB, i, bSigned), iDepth)) for i in range(iWidth)]
            if any(a is not None and b is not None and a != b for a, b in lPairs):
                return 0 if sType == "$eq" else 1
            if all(a is not None and b is not None for a, b in lPairs):
                return 1 if sType == "$eq" else 0
            return None
        return None

    def latch_value(self, oCell, iIndex, iDepth):
        """
        The value a latch settles to in test mode: that of its data, when the data is constant and the latch is not
        held closed, as the enable latch of a clock gate whose enable test mode forces. A latch with an asynchronous
        reset that test mode does not hold inactive is not constant.
        """
        lData = oCell.connections.get("D", [])
        if iIndex >= len(lData):
            return None
        iData = self.value(lData[iIndex], iDepth)
        if iData is None:
            return None
        iActive = 1 if oCell.parameter("EN_POLARITY", 1) else 0
        if self.value(oCell.connections.get("EN", [None])[0], iDepth) == 1 - iActive:
            return None
        if "ARST" in oCell.connections:
            iReset = 1 if oCell.parameter("ARST_POLARITY", 1) else 0
            if self.value(oCell.connections["ARST"][0], iDepth) != 1 - iReset:
                return None
        return iData

    def reduce(self, lBits, iDepth):
        return [self.value(b, iDepth) for b in lBits]

    # Clocks

    def clock_source(self, oNet, iDepth=0):
        """The Source of a clock net in test mode."""
        if oNet in self._dSource:
            return self._dSource[oNet]
        if iDepth > 200:
            return Source(sProblem=UNKNOWN)
        self._dSource[oNet] = Source(sProblem=UNKNOWN)
        oSource = self._clock_source(oNet, iDepth)
        self._dSource[oNet] = oSource
        return oSource

    def _clock_source(self, oNet, iDepth):
        iValue = self.value(oNet)
        if iValue is not None:
            return Source(sProblem=CONSTANT, sDetail=str(iValue))
        if not graph.is_variable(oNet):
            return Source(sProblem=UNKNOWN)
        tDriver = self.flat.driver(oNet)
        if tDriver is None:
            return Source(sProblem=UNKNOWN)
        oCell, sPort, iIndex = tDriver
        if oCell is None:
            return Source(self.flat.input_port(oNet))
        if oCell.is_black_box():
            return self.box_source(oCell, sPort, iIndex, iDepth)
        sType = oCell.type
        if sType in netlist.LATCH_TYPES:
            return Source(sProblem=FROM_LATCH, oCell=oCell, sDetail=self.flat.cell_name(oCell))
        if sType in graph.STATE_TYPES or cdc.is_clocked(oCell):
            return Source(sProblem=FROM_REGISTER, oCell=oCell, sDetail=self.flat.cell_name(oCell))
        lA = oCell.connections.get("A", [])
        lB = oCell.connections.get("B", [])
        if sType in BUFFERS:
            return self.clock_source(graph.extend(lA, iIndex, False), iDepth + 1)
        if sType in ("$not", "$_NOT_") or (sType == "$logic_not" and len(lA) == 1 and iIndex == 0):
            return inverted(self.clock_source(graph.extend(lA, iIndex, False), iDepth + 1))
        if sType in MUX_TYPES:
            oSelect = oCell.connections.get("S", [None])[0]
            iSelect = self.value(oSelect)
            if iSelect is None:
                # A multiplexer of the constants 0 and 1 is its select, or the inverted select
                tInputs = (graph.extend(lA, iIndex, False), graph.extend(lB, iIndex, False))
                if tInputs == ("0", "1"):
                    return self.clock_source(oSelect, iDepth + 1)
                if tInputs == ("1", "0"):
                    return inverted(self.clock_source(oSelect, iDepth + 1))
                return Source(sProblem=MULTIPLEXER, oCell=oCell, sDetail=self.signal_name(oSelect))
            return self.clock_source(graph.extend(lB if iSelect else lA, iIndex, False), iDepth + 1)
        if sType in AND_TYPES | OR_TYPES | {"$xor", "$_XOR_", "$xnor", "$_XNOR_", "$_NAND_", "$_NOR_", "$_ANDNOT_", "$_ORNOT_"}:
            return self.gate_source(oCell, iIndex, iDepth)
        return Source(sProblem=UNKNOWN, oCell=oCell, sDetail=self.flat.net_name(oNet))

    def gate_source(self, oCell, iIndex, iDepth):
        """The source of the clock through a gate: the one input that is not constant, inverted as the gate does."""
        sType = oCell.type
        if sType in ("$reduce_and", "$reduce_or", "$reduce_bool"):
            lInputs = list(oCell.connections.get("A", []))
        elif sType in ("$logic_and", "$logic_or"):
            lInputs = list(oCell.connections.get("A", [])) + list(oCell.connections.get("B", []))
        else:
            lInputs = [graph.extend(oCell.connections.get(s, []), iIndex, False) for s in ("A", "B")]
        lFree = [b for b in lInputs if self.value(b) is None]
        if len(lFree) != 1:
            # The clock and its gating signal both change in test mode: name the input that is not a clock
            lNames = [self.signal_name(b) for b in lFree if self.clock_source(b, iDepth + 1).problem is not None]
            lNames = lNames or [self.signal_name(b) for b in lFree[1:]]
            return Source(sProblem=GATED, oCell=oCell, sDetail=", ".join(lNames))
        oSource = self.clock_source(lFree[0], iDepth + 1)
        bInvert = sType in ("$_NAND_", "$_NOR_", "$xnor", "$_XNOR_") or (sType == "$_ORNOT_" and lFree[0] == lInputs[1])
        if sType in ("$xor", "$_XOR_", "$xnor", "$_XNOR_"):
            bInvert = bInvert != bool(self.value(lInputs[1] if lFree[0] == lInputs[0] else lInputs[0]))
        if sType == "$_ANDNOT_" and lFree[0] == lInputs[1]:
            bInvert = True
        return inverted(oSource) if bInvert else oSource

    def box_source(self, oCell, sPort, iIndex, iDepth):
        oRole = self.analysis.box_role(oCell, sPort)
        if oRole is not None and oRole.kind == "path":
            lInputs = self.analysis.path_inputs(oCell, oRole, iIndex)
            if len(lInputs) == 1:
                return self.clock_source(lInputs[0], iDepth + 1)
        if oRole is not None and oRole.kind == "clock_out":
            if oRole.relation == "same" and oRole.source:
                oNet = self.analysis.box_net(oCell, oRole.source)
                return self.clock_source(oNet, iDepth + 1)
            # A PLL: its test mode, a bypass of the oscillator, is its own
            return Source(f"{oCell!r}.{sPort}")
        return Source(sProblem=FROM_BOX, oCell=oCell, sDetail=f"{oCell!r}.{sPort}")

    def signal_name(self, oNet):
        """The name of a net, or for a net of logic without a name, the logic of the signals it comes from."""
        sName = self.flat.net_name(oNet)
        if sName.startswith("net ") and graph.is_variable(oNet):
            lSources = sorted({self.analysis.point_name(t) for t in self.analysis.sources(oNet)})
            if lSources:
                return "logic of " + ", ".join(lSources)
        return sName

    def register_name(self, oCell):
        """The name of a register or latch, with the index of its bit in a vector, such as r(2), when it has one bit."""
        sName = self.flat.cell_name(oCell)
        lLocal = [b for b in oCell.local.get("Q", []) if graph.is_variable(b)]
        if len(lLocal) != 1:
            return sName
        sBase = sName.split(".")[-1]
        dNetnames = self.flat.netlist.modules.get(oCell.module, {}).get("netnames", {})
        dNet = dNetnames.get(sBase) or dNetnames.get("\\" + sBase) or {}
        lBits = dNet.get("bits", [])
        if len(lBits) < 2 or lLocal[0] not in lBits:
            return sName
        iPosition = lBits.index(lLocal[0])
        iIndex = dNet.get("offset", 0) + (len(lBits) - 1 - iPosition if dNet.get("upto") else iPosition)
        return f"{sName}({iIndex})"

    def clocked_cells(self):
        """Yields (cell, clock pin, active level) of the registers and latches of the flat design."""
        for oCell in self.flat.cells:
            if oCell.is_black_box():
                continue
            if cdc.is_clocked(oCell) and "CLK" in oCell.connections:
                yield oCell, "CLK", 1 if oCell.parameter("CLK_POLARITY", 1) else 0
            elif oCell.type in netlist.LATCH_TYPES and "EN" in oCell.connections:
                yield oCell, "EN", 1 if oCell.parameter("EN_POLARITY", 1) else 0


def inverted(oSource):
    if oSource.problem is None:
        return Source(oSource.name, 1 - oSource.inverted)
    return oSource


def gate(sType, iA, iB):
    """The output of a two input gate, from inputs that may be unknown."""
    if sType in ("$_ANDNOT_",):
        iB = None if iB is None else 1 - iB
        sType = "$and"
    if sType in ("$_ORNOT_",):
        iB = None if iB is None else 1 - iB
        sType = "$or"
    if sType in ("$and", "$_AND_", "$_NAND_"):
        iValue = 0 if 0 in (iA, iB) else (1 if iA == 1 and iB == 1 else None)
        return iValue if sType != "$_NAND_" or iValue is None else 1 - iValue
    if sType in ("$or", "$_OR_", "$_NOR_"):
        iValue = 1 if 1 in (iA, iB) else (0 if iA == 0 and iB == 0 else None)
        return iValue if sType != "$_NOR_" or iValue is None else 1 - iValue
    if iA is None or iB is None:
        return None
    iValue = iA ^ iB
    return iValue if sType in ("$xor", "$_XOR_") else 1 - iValue


def all_of(lValues, iTrue):
    if any(v == 0 for v in lValues):
        return 0
    return iTrue if all(v == 1 for v in lValues) else None


def any_of(lValues):
    if any(v == 1 for v in lValues):
        return 1
    return 0 if all(v == 0 for v in lValues) else None


class Constants(TestMode):
    """
    The constant nets of the flat design with some nets held at a value: top inputs by name, as in test mode, and nets
    of the flat design by number, such as the output of an isolation register.
    """

    def __init__(self, oAnalysis, dValues=None, dNets=None):
        super().__init__(oAnalysis, dValues or {})
        self.nets = dict(dNets or {})

    def port_value(self, oNet):
        if oNet in self.nets:
            return self.nets[oNet]
        return super().port_value(oNet)
