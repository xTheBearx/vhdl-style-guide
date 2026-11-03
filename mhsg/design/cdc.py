# -*- coding: utf-8 -*-
"""
Clock domain crossing analysis on the flat netlist.

1. Clocks: the clock pin of each register is traced back through buffers and inverters to its source: a top input
   port, a black box output, such as a PLL, a register, which divides a clock, or logic, which gates a clock.
   Each source is a clock domain. Clocks are asynchronous to each other unless the design section groups them,
   and a clock made by a register or gated by logic belongs with the clock it comes from.
2. Crossings: the inputs of each register, other than its clock and asynchronous reset, are traced back through
   logic to the registers, memories and input ports that drive them. A source in an asynchronous domain is a
   crossing, classified by how it is synchronized.
3. Resets: the asynchronous reset of each register is traced back to its source, to check that it is released
   synchronously to the clock of the register.

Memories are not followed: data that crosses through a memory, as in an asynchronous FIFO, is safe when the
pointers that control it cross safely, which the analysis checks.
"""

import fnmatch

from mhsg.design import black_box, graph, netlist

TRANSPARENT_TYPES = {"$pos", "$buf", "$not"}
MUX_TYPES = {"$mux", "$pmux"}
MEMORY_READ_TYPES = {"$memrd", "$memrd_v2"}
# Ports of registers that are not data: the clock and the asynchronous set and reset
CONTROL_PORTS = {"CLK", "ARST", "SET", "CLR", "AL", "AD"}
RESET_PORTS = ("ARST", "SET", "CLR", "AL")

SYNCHRONIZED = "synchronized"
GRAY = "gray-coded bus"
QUALIFIED = "qualified by enable"
BUS = "bus synchronized bit by bit"
LOGIC = "logic before synchronizer"
UNSYNCHRONIZED = "unsynchronized"
WAIVED = "waived"
SAFE = (SYNCHRONIZED, GRAY, QUALIFIED)
HAZARDS = (BUS, LOGIC)


def is_register(oCell):
    return oCell is not None and oCell.type in netlist.FLIP_FLOP_TYPES


def is_clocked(oCell):
    """A register, or a memory port with a clock."""
    if oCell is None:
        return False
    if is_register(oCell):
        return True
    return oCell.type in MEMORY_READ_TYPES | {"$memwr", "$memwr_v2"} and oCell.parameter("CLK_ENABLE", 1) != 0


class Clock:
    """A clock domain: the source of a clock."""

    def __init__(self, sKey, sKind, sName, oNet, oCell=None):
        # port, box (a black box output), register (a divided clock), logic (a clock made by logic)
        self.key = sKey
        self.kind = sKind
        self.name = sName
        self.net = oNet
        self.cell = oCell
        # The clock a divided or gated clock comes from
        self.parent = None
        self.gates = []
        self.group = sKey
        self.registers = 0

    def __repr__(self):
        return self.name


class Crossing:
    """A register that captures data from another clock domain."""

    def __init__(self, oCell, sName, oDomain):
        self.cell = oCell
        self.name = sName
        self.clock = oDomain
        self.sources = {}
        self.status = None
        self.stages = 0
        self.detail = ""
        self.justification = None

    def source_text(self):
        return ", ".join(f"{s} ({o.name})" for s, o in sorted(self.sources.items()))


class ResetFinding:
    def __init__(self, sKind, oCell, sReset, lCells, sDetail=""):
        # raw (released asynchronously), crossing (synchronized to another clock), generated, shared
        self.kind = sKind
        self.cell = oCell
        self.reset = sReset
        self.cells = lCells
        self.detail = sDetail


class Analysis:
    def __init__(self, oFlat, dConstraints=None, fLocate=None, oBlackBoxes=None):
        self.flat = oFlat
        # The declarations of the black boxes: nothing is assumed about a black box that has none
        self.box_library = oBlackBoxes if oBlackBoxes is not None else black_box.Library()
        self.boxes = {id(o): black_box.Instance(o, self.box_library.find(o.type, repr(o))) for o in oFlat.cells if o.is_black_box()}
        self.box_problems = []
        self.box_synchronizers = []
        # Returns (file, line) of a cell and the signal it drives; the location of the cell itself by default
        self.locate = fLocate or self.cell_location
        self.constraints = dConstraints or {}
        self.clocks = {}
        self.cell_clock = {}
        self.crossings = []
        self.resets = []
        self.clock_as_data = []
        self.shared = []
        # (registers, signals) where separately synchronized signals meet again
        self.reconvergences = []
        self.waiver_errors = []
        self._dStrip = {}
        self._dSources = {}
        self._check_boxes()
        self._find_clocks()
        self._find_crossings()
        self._find_resets()
        self._find_clock_as_data()
        self._apply_waivers()

    # Black boxes

    def box_role(self, oCell, sPort):
        """The declared role of a port of a black box, or None when it has none."""
        oInstance = self.boxes.get(id(oCell))
        return oInstance.role(sPort) if oInstance is not None else None

    def box_net(self, oCell, sPort, iIndex=0):
        """The net on a bit of a port of a cell, matching the port name in any case; None if there is none."""
        for sName, lNets in oCell.connections.items():
            if sName.lower() == str(sPort).lower():
                return lNets[min(iIndex, len(lNets) - 1)] if lNets else None
        return None

    def box_clock(self, oCell, sPin):
        """The Clock on a clock pin of a black box."""
        oNet = self.box_net(oCell, sPin)
        return self.trace_clock(oNet) if graph.is_variable(oNet) else None

    def _check_boxes(self):
        """Every black box must be declared, with a role for every port; a static port needs reviewed_by."""
        dTypes = {}
        for oInstance in self.boxes.values():
            dTypes.setdefault(oInstance.cell.type, []).append(oInstance)
        for sType, lInstances in sorted(dTypes.items(), key=lambda t: t[0].lower()):
            lUndeclared = [o for o in lInstances if not o.declared()]
            if lUndeclared:
                self.box_problems.append((lUndeclared[0].cell, f"Black box {sType} has no declaration of its clock domain behaviour", len(lUndeclared)))
            lSeen = []
            for oInstance in lInstances:
                if not oInstance.declared():
                    continue
                for sProblem in oInstance.problems(black_box.port_list(self.flat, oInstance.cell)):
                    if sProblem not in lSeen:
                        lSeen.append(sProblem)
                        self.box_problems.append((oInstance.cell, f"Black box {sType}: {sProblem}", 1))

    # Following nets

    def through_transparent(self, oNet):
        """Follows a net back through buffers and inverters; returns (net, cells passed)."""
        lCells = []
        setSeen = set()
        while graph.is_variable(oNet) and oNet not in setSeen:
            setSeen.add(oNet)
            tDriver = self.flat.driver(oNet)
            if tDriver is None or tDriver[0] is None or tDriver[0].type not in TRANSPARENT_TYPES:
                break
            oCell, _, iIndex = tDriver
            lCells.append(oCell)
            oNet = graph.extend(oCell.connections.get("A", []), iIndex, oCell.parameter("A_SIGNED"))
        return oNet, lCells

    def comb_inputs(self, oCell, sPort, iIndex):
        """The nets an output bit of a logic cell depends on, bit by bit where the cell allows it."""
        dCell = {"type": oCell.type, "parameters": oCell.cell.get("parameters", {}), "connections": oCell.connections}
        sType = oCell.type
        lA = oCell.connections.get("A", [])
        lB = oCell.connections.get("B", [])
        if sType in graph.BITWISE_TYPES:
            lReturn = [graph.extend(lA, iIndex, graph.parameter(dCell, "A_SIGNED")), graph.extend(lB, iIndex, graph.parameter(dCell, "B_SIGNED"))]
        elif sType == "$mux":
            lReturn = [graph.extend(lA, iIndex, False), graph.extend(lB, iIndex, False)] + oCell.connections.get("S", [])
        elif sType == "$pmux":
            iWidth = graph.parameter(dCell, "WIDTH", len(lA)) or 1
            lReturn = [graph.extend(lA, iIndex, False)] + lB[iIndex::iWidth] + oCell.connections.get("S", [])
        elif sType in graph.ARITHMETIC_TYPES:
            lReturn = lA[: iIndex + 1] + lB[: iIndex + 1]
        else:
            lReturn = [b for sInput, lBits in oCell.connections.items() if self.flat.direction(oCell, sInput) == "input" for b in lBits]
        return [b for b in lReturn if graph.is_variable(b)]

    def sources(self, oNet):
        """
        Returns the set of points that drive a net through logic: (cell, port, index) for registers, memory reads and
        black boxes, (None, port, index) for top inputs. Memoized; a combinational loop gives a partial set.
        """
        if oNet in self._dSources:
            return self._dSources[oNet]
        lStack = [(oNet, False)]
        setVisiting = set()
        while lStack:
            oCurrent, bDone = lStack.pop()
            if oCurrent in self._dSources or (not bDone and oCurrent in setVisiting):
                continue
            tDriver = self.flat.driver(oCurrent)
            if tDriver is None:
                self._dSources[oCurrent] = frozenset()
                continue
            oCell, sPort, iIndex = tDriver
            oRole = self.box_role(oCell, sPort) if oCell is not None and oCell.is_black_box() else None
            if oRole is not None and oRole.kind == "path":
                # A declared path through a black box, such as an input buffer, is followed like logic
                lInputs = self.path_inputs(oCell, oRole, iIndex)
            elif oCell is None or oCell.is_black_box() or is_clocked(oCell) or oCell.type in MEMORY_READ_TYPES or oCell.type in graph.STATE_TYPES:
                self._dSources[oCurrent] = frozenset([tDriver])
                continue
            else:
                lInputs = self.comb_inputs(oCell, sPort, iIndex)
            if not bDone:
                setVisiting.add(oCurrent)
                lStack.append((oCurrent, True))
                lStack.extend((b, False) for b in lInputs if b not in self._dSources and b not in setVisiting)
                continue
            setResult = set()
            for oInput in lInputs:
                setResult |= self._dSources.get(oInput, frozenset())
            self._dSources[oCurrent] = frozenset(setResult)
        return self._dSources[oNet]

    def path_inputs(self, oCell, oRole, iIndex):
        """The input nets an output bit of a black box follows: the same bit of inputs as wide as needed, else all bits."""
        lReturn = []
        for sInput in oRole.inputs:
            lNets = next((l for s, l in oCell.connections.items() if s.lower() == sInput.lower()), [])
            lReturn += [lNets[iIndex]] if iIndex < len(lNets) and len(lNets) > 1 else list(lNets)
        return [b for b in lReturn if graph.is_variable(b)]

    def strip(self, oCell, iIndex, sPort="D"):
        """
        Follows the data input bit of a register back through the multiplexers that only hold its value, such as a
        clock enable, or load a constant, such as a reset. Returns (net, multiplexers holding the value, cells passed).
        """
        tKey = (id(oCell), sPort, iIndex)
        if tKey in self._dStrip:
            return self._dStrip[tKey]
        lQ = oCell.connections.get("Q", [])
        oOwn = lQ[iIndex] if iIndex < len(lQ) else None
        lD = oCell.connections.get(sPort, [])
        oNet = lD[iIndex] if iIndex < len(lD) else None
        lHolds = []
        lCells = []
        setSeen = set()
        while graph.is_variable(oNet) and oNet not in setSeen:
            setSeen.add(oNet)
            tDriver = self.flat.driver(oNet)
            if tDriver is None or tDriver[0] is None:
                break
            oDriver, _, iOut = tDriver
            if oDriver.type in ("$pos", "$buf"):
                lCells.append(oDriver)
                oNet = graph.extend(oDriver.connections.get("A", []), iOut, False)
                continue
            if oDriver.type != "$mux":
                break
            oA = graph.extend(oDriver.connections.get("A", []), iOut, False)
            oB = graph.extend(oDriver.connections.get("B", []), iOut, False)
            if oA == oOwn or oB == oOwn:
                lHolds.append(oDriver)
                lCells.append(oDriver)
                oNet = oB if oA == oOwn else oA
            elif not graph.is_variable(oA) and graph.is_variable(oB):
                lCells.append(oDriver)
                oNet = oB
            elif not graph.is_variable(oB) and graph.is_variable(oA):
                lCells.append(oDriver)
                oNet = oA
            else:
                break
        self._dStrip[tKey] = (oNet, lHolds, lCells)
        return self._dStrip[tKey]

    # Clocks

    def trace_clock(self, oNet):
        """Returns the Clock of a clock net, creating it the first time a source is seen."""
        oRoot, _ = self.through_transparent(oNet)
        if not graph.is_variable(oRoot):
            return None
        tDriver = self.flat.driver(oRoot)
        if tDriver is None:
            return self.clock(f"net {oRoot}", "undriven", self.flat.net_name(oRoot), oRoot)
        oCell, sPort, iIndex = tDriver
        if oCell is None:
            return self.clock("port " + self.flat.input_port(oRoot), "port", self.flat.input_port(oRoot), oRoot)
        if oCell.is_black_box():
            sName = f"{oCell!r}.{sPort}" + (f"({iIndex})" if len(oCell.connections.get(sPort, [])) > 1 else "")
            oRole = self.box_role(oCell, sPort)
            if oRole is not None and oRole.kind == "path":
                lInputs = self.path_inputs(oCell, oRole, iIndex)
                return self.trace_clock(lInputs[0]) if lInputs else None
            if oRole is not None and oRole.kind == "clock_out" and oRole.relation == "same":
                # A clock buffer: the clock of its input
                return self.box_clock(oCell, oRole.source)
            oDomain = self.clock("box " + sName, "box", sName, oRoot, oCell)
            if oRole is not None and oRole.kind == "clock_out" and oRole.relation == "derived" and oDomain.parent is None:
                oDomain.parent = False
                oDomain.parent = self.box_clock(oCell, oRole.source)
            return oDomain
        if is_clocked(oCell) or oCell.type in graph.STATE_TYPES:
            oDomain = self.clock("register " + self.flat.cell_name(oCell), "register", self.flat.cell_name(oCell), oRoot, oCell)
            if oDomain.parent is None and "CLK" in oCell.connections:
                oDomain.parent = False
                oDomain.parent = self.trace_clock(oCell.connections["CLK"][0])
            return oDomain
        oDomain = self.clock("logic " + self.flat.net_name(oRoot), "logic", self.flat.net_name(oRoot), oRoot, oCell)
        if oDomain.parent is None:
            oDomain.parent = False
            lUpstream = [self.trace_clock(b) for b in self.upstream_roots(oRoot)]
            lUpstream = [o for o in lUpstream if o is not None and o.kind in ("port", "box", "register")]
            # Prefer sources that clock registers directly; a gate also reads its enable
            lClocks = [o for o in lUpstream if o.registers > 0] or [o for o in lUpstream if o.kind != "register"]
            oDomain.parent = lClocks[0] if lClocks else None
            oDomain.gates = [oCell]
        return oDomain

    def upstream_roots(self, oNet):
        """The nets of registers, ports and black boxes that drive a net through logic."""
        lReturn = []
        for oCell, sPort, iIndex in self.sources(oNet):
            if oCell is None:
                lReturn.append(self.flat.top_ports[sPort][1][iIndex])
            else:
                lReturn.append(oCell.connections[sPort][iIndex])
        return lReturn

    def clock(self, sKey, sKind, sName, oNet, oCell=None):
        if sKey not in self.clocks:
            self.clocks[sKey] = Clock(sKey, sKind, sName, oNet, oCell)
        return self.clocks[sKey]

    def _find_clocks(self):
        # Direct clocks first, so a gate can tell its clock input from its enable
        lClocked = [o for o in self.flat.cells if is_clocked(o) and "CLK" in o.connections]
        lDeferred = []
        for oCell in lClocked:
            oRoot, _ = self.through_transparent(oCell.connections["CLK"][0])
            tDriver = self.flat.driver(oRoot) if graph.is_variable(oRoot) else None
            if tDriver is not None and tDriver[0] is not None and not tDriver[0].is_black_box() and not is_clocked(tDriver[0]):
                lDeferred.append(oCell)
                continue
            oDomain = self.trace_clock(oCell.connections["CLK"][0])
            self.cell_clock[id(oCell)] = oDomain
            if oDomain is not None:
                oDomain.registers += 1
        for oCell in lDeferred:
            oDomain = self.trace_clock(oCell.connections["CLK"][0])
            self.cell_clock[id(oCell)] = oDomain
            if oDomain is not None:
                oDomain.registers += 1
        self._group_clocks()

    def _group_clocks(self):
        """Puts each clock in a group of synchronous clocks: named groups, and divided or gated clocks with their source."""
        dNames = {}
        for sName, sSource in (self.constraints.get("clocks") or {}).items():
            for oDomain in self.clocks.values():
                if oDomain.name == str(sSource) or fnmatch.fnmatchcase(oDomain.name, str(sSource)):
                    oDomain.name = str(sName)
        for oDomain in self.clocks.values():
            dNames.setdefault(oDomain.name.lower(), []).append(oDomain)
        dParent = {}

        def root(sKey):
            while dParent.get(sKey, sKey) != sKey:
                sKey = dParent[sKey]
            return sKey

        def join(oFirst, oSecond):
            sFirst, sSecond = root(oFirst.key), root(oSecond.key)
            if sFirst != sSecond:
                dParent[sSecond] = sFirst

        for oDomain in self.clocks.values():
            if oDomain.parent:
                join(oDomain.parent, oDomain)
            for oSame in dNames[oDomain.name.lower()]:
                join(oDomain, oSame)
        for lGroup in self.constraints.get("clock_groups") or []:
            lMembers = [o for s in lGroup for o in dNames.get(str(s).lower(), [])]
            for oMember in lMembers[1:]:
                join(lMembers[0], oMember)
        for oDomain in self.clocks.values():
            oDomain.group = root(oDomain.key)

    def domain_of(self, tPoint):
        """Returns the Clock of a source point, the string "async" for an asynchronous input, or None if unknown."""
        oCell, sPort, _ = tPoint
        if oCell is None:
            dInputs = {str(k).lower(): str(v) for k, v in (self.constraints.get("inputs") or {}).items()}
            sDomain = dInputs.get(sPort.lower())
            if sDomain is None:
                return None
            if sDomain.lower() == "async":
                return "async"
            for oDomain in self.clocks.values():
                if oDomain.name.lower() == sDomain.lower():
                    return oDomain
            return None
        if oCell.is_black_box():
            return self.box_domain(oCell, sPort)
        return self.cell_clock.get(id(oCell))

    def box_domain(self, oCell, sPort):
        """The clock domain of a black box output: from its role; None for static, unknown or undeclared outputs."""
        oRole = self.box_role(oCell, sPort)
        if oRole is None:
            return None
        if oRole.kind in ("sync", "synchronized"):
            return self.box_clock(oCell, oRole.clock)
        if oRole.kind == "reset_out":
            return self.box_clock(oCell, oRole.clock) if oRole.release == "sync" else "async"
        if oRole.kind == "async":
            return "async"
        return None

    @staticmethod
    def related(oFirst, oSecond):
        if oFirst is None or oSecond is None:
            return True
        if oFirst == "async" or oSecond == "async":
            return False
        return oFirst.group == oSecond.group

    # Crossings

    def point_name(self, tPoint):
        oCell, sPort, iIndex = tPoint
        if oCell is None:
            return sPort if len(self.flat.top_ports[sPort][1]) == 1 else f"{sPort}({iIndex})"
        if oCell.is_black_box():
            return f"{oCell!r}.{sPort}"
        return self.flat.cell_name(oCell, sPort if sPort in ("Q", "DATA") else "Q")

    def _find_crossings(self):
        lRegisters = [o for o in self.flat.cells if is_register(o) and self.cell_clock.get(id(o)) is not None]
        # The register bits whose stripped data input is each net: the stages that may follow a register
        self._dFollowers = {}
        for oCell in lRegisters:
            for iIndex in range(len(oCell.connections.get("Q", []))):
                oNet, _, lCells = self.strip(oCell, iIndex)
                if graph.is_variable(oNet):
                    self._dFollowers.setdefault(oNet, []).append((oCell, iIndex, lCells))
        dCrossings = {}
        for oCell in lRegisters:
            oDomain = self.cell_clock[id(oCell)]
            for sPort, lNets in oCell.connections.items():
                if sPort in CONTROL_PORTS or sPort == "Q" or self.flat.direction(oCell, sPort) != "input":
                    continue
                for iIndex, oNet in enumerate(lNets):
                    if not graph.is_variable(oNet):
                        continue
                    lForeign = [t for t in self.sources(oNet) if not self.related(self.domain_of(t), oDomain)]
                    if not lForeign:
                        continue
                    oCrossing = dCrossings.get(id(oCell))
                    if oCrossing is None:
                        oCrossing = Crossing(oCell, self.flat.cell_name(oCell), oDomain)
                        dCrossings[id(oCell)] = oCrossing
                        oCrossing.bits = []
                    for tPoint in lForeign:
                        oSource = self.domain_of(tPoint)
                        oCrossing.sources[self.point_name(tPoint)] = oSource if oSource != "async" else Clock("async", "async", "async", None)
                    oCrossing.bits.append((sPort, iIndex, lForeign))
        for oCrossing in dCrossings.values():
            self.classify(oCrossing)
            self.crossings.append(oCrossing)
        self._find_box_crossings()
        self._find_buses()
        self.crossings.sort(key=lambda o: o.name)
        self.reconvergences = self._find_reconvergence(False)
        # Meetings found only when synchronous resets are followed, listed in the report and reported on request
        lData = {(self.endpoint_name(t[0][0]), tuple(x[1] for x in t[1])) for t in self.reconvergences}
        self.reset_reconvergences = [t for t in self._find_reconvergence(True) if (self.endpoint_name(t[0][0]), tuple(x[1] for x in t[1])) not in lData]

    def _find_box_crossings(self):
        """
        An input of a black box timed by one of its clocks is like the input of a register: data from another domain
        must be synchronized before it. Outputs synchronized inside a black box are listed for manual review.
        """
        for oInstance in self.boxes.values():
            oCell = oInstance.cell
            for sPort, lNets in sorted(oCell.connections.items()):
                oRole = oInstance.role(sPort)
                if oRole is None:
                    continue
                if oRole.kind == "synchronized":
                    oSource = None
                    if oRole.source:
                        oSourceRole = oInstance.role(oRole.source)
                        oSource = self.box_clock(oCell, oSourceRole.clock) if oSourceRole is not None and oSourceRole.kind == "sync" else "async"
                    self.box_synchronizers.append((oInstance, sPort, oRole, oSource, self.box_clock(oCell, oRole.clock)))
                    continue
                if oRole.kind != "sync" or self.flat.direction(oCell, sPort) != "input":
                    continue
                oDomain = self.box_clock(oCell, oRole.clock)
                if oDomain is None:
                    continue
                oCrossing = None
                for oNet in lNets:
                    if not graph.is_variable(oNet):
                        continue
                    lForeign = [t for t in self.sources(oNet) if not self.related(self.domain_of(t), oDomain)]
                    if not lForeign:
                        continue
                    if oCrossing is None:
                        oCrossing = Crossing(oCell, f"{oCell!r}.{sPort}", oDomain)
                        oCrossing.status = UNSYNCHRONIZED
                        oCrossing.detail = f"into an input of black box {oCell.type} timed by {oRole.clock}"
                        oCrossing.bits = []
                        self.crossings.append(oCrossing)
                    for tPoint in lForeign:
                        oSource = self.domain_of(tPoint)
                        oCrossing.sources[self.point_name(tPoint)] = oSource if oSource != "async" else Clock("async", "async", "async", None)
        for oInstance in self.boxes.values():
            if any(o.archetype == "dual_clock_fifo" for o in oInstance.declarations):
                self.box_synchronizers.append((oInstance, None, None, None, None))

    def stages_after(self, oCell, iIndex):
        """Returns the number of registers in the same domain that follow a register bit as a chain, each feeding only the next."""
        return self.chain(oCell, iIndex)[0]

    def chain(self, oCell, iIndex):
        """
        Follows a register bit through the registers of the same domain that follow it, each fed only by the one
        before. Returns (number of stages, last register, its bit), the last stage being the synchronizer output.
        """
        iStages = 1
        oDomain = self.cell_clock.get(id(oCell))
        setSeen = {(id(oCell), iIndex)}
        while True:
            oQ = oCell.connections["Q"][iIndex]
            lNext = [t for t in self._dFollowers.get(oQ, []) if self.cell_clock.get(id(t[0])) is oDomain and t[0] is not oCell]
            if len(lNext) != 1:
                return iStages, oCell, iIndex
            oNext, iNext, lCells = lNext[0]
            setPath = {id(o) for o in lCells} | {id(oNext)}
            if any(t[0] is None or id(t[0]) not in setPath for t in self.flat.readers.get(oQ, [])):
                # The output of the stage is also used elsewhere
                return iStages, oCell, iIndex
            if (id(oNext), iNext) in setSeen:
                return iStages, oCell, iIndex
            setSeen.add((id(oNext), iNext))
            iStages += 1
            oCell, iIndex = oNext, iNext

    def is_synchronizer_output(self, oNet):
        """Returns whether a net is the output of the second or a later stage of a synchronizer."""
        tDriver = self.flat.driver(oNet)
        if tDriver is None or not is_register(tDriver[0]):
            return False
        oCell, _, iIndex = tDriver
        oDomain = self.cell_clock.get(id(oCell))
        oData, _, _ = self.strip(oCell, iIndex)
        tPrevious = self.flat.driver(oData) if graph.is_variable(oData) else None
        if tPrevious is None or not is_register(tPrevious[0]) or self.cell_clock.get(id(tPrevious[0])) is not oDomain:
            return False
        oFirst, _, iFirst = tPrevious
        oFirstData, _, _ = self.strip(oFirst, iFirst)
        if not graph.is_variable(oFirstData):
            return False
        return any(not self.related(self.domain_of(t), oDomain) for t in self.sources(oFirstData))

    def qualified(self, oCell, iIndex, oDomain):
        """Returns whether a register bit is loaded only when an enable synchronized to its own clock allows it."""
        _, lHolds, _ = self.strip(oCell, iIndex)
        for oMux in lHolds:
            lSelect = [b for b in oMux.connections.get("S", []) if graph.is_variable(b)]
            lPoints = [t for b in lSelect for t in self.sources(b)]
            if not lPoints or any(not self.related(self.domain_of(t), oDomain) for t in lPoints):
                continue
            lNets = [t[0].connections[t[1]][t[2]] for t in lPoints if t[0] is not None and not t[0].is_black_box()]
            if any(self.is_synchronizer_output(b) for b in lNets):
                return True
        return False

    def classify(self, oCrossing):
        lStatus = []
        oCrossing.stages = 0
        oCrossing.first_stages = []
        for sPort, iIndex, lForeign in oCrossing.bits:
            if sPort != "D":
                # An enable or synchronous reset from another domain
                lStatus.append(UNSYNCHRONIZED)
                continue
            oNet, _, _ = self.strip(oCrossing.cell, iIndex)
            tDriver = self.flat.driver(oNet) if graph.is_variable(oNet) else None
            bDirect = tDriver is not None and tDriver in lForeign and tDriver[0] is not None and is_register(tDriver[0])
            iStages = self.stages_after(oCrossing.cell, iIndex)
            oCrossing.stages = max(oCrossing.stages, iStages)
            if bDirect and iStages >= 2:
                lStatus.append(SYNCHRONIZED)
                oCrossing.first_stages.append((iIndex, tDriver))
            elif self.qualified(oCrossing.cell, iIndex, oCrossing.clock):
                lStatus.append(QUALIFIED)
            elif iStages >= 2:
                lStatus.append(LOGIC)
            else:
                lStatus.append(UNSYNCHRONIZED)
        for sStatus in (UNSYNCHRONIZED, LOGIC, QUALIFIED, SYNCHRONIZED):
            if sStatus in lStatus:
                oCrossing.status = sStatus
                break
        if oCrossing.status == SYNCHRONIZED:
            oCrossing.detail = f"{oCrossing.stages} stages"
        elif oCrossing.status == UNSYNCHRONIZED:
            oCrossing.detail = "captured without a synchronizer" if oCrossing.stages < 2 else "enable or reset from another clock domain"
        elif oCrossing.status == LOGIC:
            oCrossing.detail = "logic between the clock domains can glitch into the first stage"

    def _find_buses(self):
        """Bits of one source register synchronized one by one can arrive in different cycles, unless they are gray coded."""
        dBySource = {}
        for oCrossing in self.crossings:
            if oCrossing.status != SYNCHRONIZED:
                continue
            for _, tSource in oCrossing.first_stages:
                tKey = (id(tSource[0]), oCrossing.clock.group)
                dBySource.setdefault(tKey, []).append((oCrossing, tSource))
        for lMembers in dBySource.values():
            setBits = {t[1][2] for t in lMembers}
            if len(setBits) < 2:
                continue
            oSource = lMembers[0][1][0]
            sStatus = GRAY if self.gray_coded(oSource) else BUS
            for oCrossing, _ in lMembers:
                oCrossing.status = sStatus
                oCrossing.detail = f"{len(setBits)} bits of {self.flat.cell_name(oSource)}" + (", gray coded" if sStatus == GRAY else " cross separately")

    def _find_reconvergence(self, bFollowResets):
        """
        Each synchronizer delivers its signal one or two destination cycles after the change, at random, so two
        synchronized signals can be seen in a combination the source never had, and two synchronizers of the same
        signal can disagree. Every synchronizer gets a tag on its output, and the tags flow forward through logic,
        registers and memories of the destination domain. Where tags of two synchronizers from the same source
        domain meet for the first time, at a register, a memory, a black box input or an output, is a reconvergence.
        The bits of one bus share a tag: a gray-coded bus is meant to be combined, and design_009 reports other buses.
        """
        self.sync_tags = []
        dSeeds = {}
        dBusTags = {}
        for oCrossing in self.crossings:
            sStatus = getattr(oCrossing, "original_status", None) or oCrossing.status
            if sStatus not in (SYNCHRONIZED, GRAY, BUS):
                continue
            for iIndex, tSource in getattr(oCrossing, "first_stages", []):
                oSourceDomain = self.domain_of(tSource)
                if oSourceDomain is None:
                    continue
                sGroup = "async" if oSourceDomain == "async" else oSourceDomain.group
                if sStatus in (GRAY, BUS):
                    tBus = (id(tSource[0]), oCrossing.clock.group)
                    if tBus not in dBusTags:
                        dBusTags[tBus] = len(self.sync_tags)
                        self.sync_tags.append((self.flat.cell_name(tSource[0]), oCrossing.name, oSourceDomain, (sGroup, oCrossing.clock.group)))
                    iTag = dBusTags[tBus]
                else:
                    sSource = self.point_name(tSource)
                    sFirst = oCrossing.name
                    if len(tSource[0].connections.get("Q", [])) > 1:
                        sSource += f"({tSource[2]})"
                    if len(oCrossing.cell.connections.get("Q", [])) > 1:
                        sFirst += f"({iIndex})"
                    iTag = len(self.sync_tags)
                    self.sync_tags.append((sSource, sFirst, oSourceDomain, (sGroup, oCrossing.clock.group)))
                _, oLast, iLast = self.chain(oCrossing.cell, iIndex)
                tNode = ("r", id(oLast), iLast)
                dSeeds[tNode] = dSeeds.get(tNode, 0) | (1 << iTag)
        # Outputs synchronized inside black boxes, such as vendor synchronizer macros, are synchronizers too
        for oInstance, sPort, oRole, oSource, oDestination in self.box_synchronizers:
            if sPort is None or oDestination is None:
                continue
            sGroup = oSource.group if isinstance(oSource, Clock) else "async"
            iTag = len(self.sync_tags)
            sFrom = f"{oInstance.cell!r}.{oRole.source}" if oRole.source else f"{oInstance.cell!r}"
            self.sync_tags.append((sFrom, f"{oInstance.cell!r}.{sPort}", oSource if isinstance(oSource, Clock) else "async", (sGroup, oDestination.group)))
            tNode = ("b", id(oInstance.cell), sPort.lower())
            dSeeds[tNode] = dSeeds.get(tNode, 0) | (1 << iTag)
        if len(self.sync_tags) < 2:
            return []
        lReturn = []
        dDependencies, dGroups = self._tag_graph(bFollowResets)
        dTags = self._propagate_tags(dDependencies, dSeeds)
        if not bFollowResets:
            # Kept for checking how far each synchronizer reaches
            self.tag_masks = dTags
        dFound = {}

        def check(tEndpoint, lSets):
            iNew = new_meetings(lSets, self.sync_tags)
            if iNew:
                dFound.setdefault(iNew, []).append(tEndpoint)

        # Tags that circulate in a feedback loop, such as a state machine, reach every register of the loop, so a
        # meeting inside a loop is judged on the loop as a whole: on the tags that enter it from outside
        lNodes = sorted(set(dDependencies) | set(dSeeds), key=repr)
        for lComponent in graph.strongly_connected(lNodes, lambda t: dDependencies.get(t, ())):
            setComponent = set(lComponent)
            lSets = []
            dEntries = {}
            for tNode in lComponent:
                lEntering = [dSeeds.get(tNode, 0)] + [dTags.get(t, 0) for t in dDependencies.get(tNode, ()) if t not in setComponent]
                lSets += lEntering
                dEntries[tNode] = 0
                for iSet in lEntering:
                    dEntries[tNode] |= iSet
            iNew = new_meetings(lSets, self.sync_tags)
            if not iNew:
                continue
            # Report where the meeting tags enter the loop, or at the node itself
            lPlaces = [t for t in lComponent if dEntries[t] & iNew] if len(lComponent) > 1 else lComponent
            for tNode in lPlaces:
                if tNode[0] in ("r", "m", "d"):
                    dFound.setdefault(iNew, []).append(("node", tNode))
        # Each bit of a black box input and of an output of the design, where tags leave the analysis; what a black
        # box does with its inputs is not known, so only logic before it counts
        for oCell in self.flat.cells:
            if oCell.is_black_box():
                for oNet in self.input_nets(oCell):
                    check(("box", oCell), [dTags.get(t, 0) for t in self.point_nodes(self.sources(oNet))])
        for sPort, (sDirection, lNets) in self.flat.top_ports.items():
            if sDirection in ("output", "inout"):
                for iIndex, oNet in enumerate(lNets):
                    if graph.is_variable(oNet):
                        sName = sPort if len(lNets) == 1 else f"{sPort}({iIndex})"
                        check(("port", sName, [oNet]), [dTags.get(t, 0) for t in self.point_nodes(self.sources(oNet))])
        # One finding for each place: the bits of one register, memory, black box or output port together
        dPlaces = {}
        for iMask, lEndpoints in dFound.items():
            for tEndpoint in lEndpoints:
                if tEndpoint[0] == "node":
                    oPlace = dGroups["cells"].get(tEndpoint[1]) or self._node_cell.get(tEndpoint[1])
                elif tEndpoint[0] == "box":
                    oPlace = tEndpoint[1]
                else:
                    oPlace = ("port", tEndpoint[1].split("(")[0], tEndpoint[2])
                if oPlace is None:
                    continue
                tKey = (id(oPlace) if not isinstance(oPlace, tuple) else oPlace[1], iMask)
                if tKey not in dPlaces:
                    dPlaces[tKey] = (oPlace, iMask)
        for oPlace, iMask in dPlaces.values():
            lSignals = [self.sync_tags[i] for i in range(len(self.sync_tags)) if iMask >> i & 1]
            lReturn.append(([oPlace], lSignals))
        lReturn.sort(key=lambda t: self.endpoint_name(t[0][0]))
        return lReturn

    def reconvergence_location(self, oEndpoint):
        """(file, line) of a reconvergence point; for an output, of the logic that drives it."""
        if isinstance(oEndpoint, tuple):
            for oNet in oEndpoint[2]:
                tDriver = self.flat.driver(oNet) if graph.is_variable(oNet) else None
                if tDriver is not None and tDriver[0] is not None:
                    return self.locate(tDriver[0], oEndpoint[1])
            return None, 0
        return self.locate(oEndpoint, self.endpoint_name(oEndpoint).split(".")[-1])

    def endpoint_clock(self, oEndpoint):
        oDomain = None if isinstance(oEndpoint, tuple) else self.cell_clock.get(id(oEndpoint))
        return oDomain.name if oDomain is not None else None

    def endpoint_name(self, oEndpoint):
        """The name of a reconvergence point: a register or memory cell, a black box, or an output port."""
        if isinstance(oEndpoint, tuple):
            return oEndpoint[1]
        if oEndpoint.is_black_box() or oEndpoint.type in ("$memwr", "$memwr_v2"):
            return repr(oEndpoint) if oEndpoint.is_black_box() else self.flat.cell_name(oEndpoint, "DATA")
        return self.flat.cell_name(oEndpoint)

    def input_nets(self, oCell):
        return [b for s, l in oCell.connections.items() if self.flat.direction(oCell, s) == "input" for b in l if graph.is_variable(b)]

    def point_nodes(self, setPoints):
        """The tag nodes of source points: register bits and memory read ports."""
        lReturn = []
        for oCell, sPort, iIndex in setPoints:
            if oCell is not None and oCell.is_black_box():
                oRole = self.box_role(oCell, sPort)
                if oRole is not None and oRole.kind == "synchronized":
                    lReturn.append(("b", id(oCell), sPort.lower()))
                continue
            if oCell is None:
                continue
            if is_register(oCell):
                lReturn.append(("r", id(oCell), iIndex))
            elif oCell.type in MEMORY_READ_TYPES:
                lReturn.append(("d", id(oCell)))
        return lReturn

    def split_inputs(self, oCell, iIndex):
        """
        Splits the data input of a register bit into data and synchronous reset: follows the multiplexers in front of
        the register, where the select of one that keeps the value, an enable, is data, and the select of one that
        loads a constant, a reset, set or clear, is a reset. Returns (data nets, reset nets).
        """
        lQ = oCell.connections.get("Q", [])
        lD = oCell.connections.get("D", [])
        oOwn = lQ[iIndex] if iIndex < len(lQ) else None
        oNet = lD[iIndex] if iIndex < len(lD) else None
        lData = []
        lReset = []
        setSeen = set()
        while graph.is_variable(oNet) and oNet not in setSeen:
            setSeen.add(oNet)
            tDriver = self.flat.driver(oNet)
            if tDriver is None or tDriver[0] is None:
                break
            oMux, _, iOut = tDriver
            if oMux.type in ("$pos", "$buf"):
                oNet = graph.extend(oMux.connections.get("A", []), iOut, False)
                continue
            if oMux.type != "$mux":
                break
            oA = graph.extend(oMux.connections.get("A", []), iOut, False)
            oB = graph.extend(oMux.connections.get("B", []), iOut, False)
            lSelect = [b for b in oMux.connections.get("S", []) if graph.is_variable(b)]
            if oA == oOwn or oB == oOwn:
                lData += lSelect
                oNet = oB if oA == oOwn else oA
            elif not graph.is_variable(oA) or not graph.is_variable(oB):
                lReset += lSelect
                oNet = oB if not graph.is_variable(oA) else oA
            else:
                break
        if graph.is_variable(oNet):
            lData.append(oNet)
        return lData, lReset

    def _tag_graph(self, bFollowResets=False):
        """
        Returns ({node: nodes it depends on}, {"cells": {node: cell}}) for register bits ("r"), memory read ports ("d")
        and memories ("m"). A node only depends on nodes of its own clock domain: the rest are crossings.
        Unless bFollowResets, a synchronous reset is not followed: a node that loads a constant into two or more
        registers through the multiplexers in front of them.
        """
        dDependencies = {}
        dCells = {}
        dDomain = {}

        def group(oCell):
            oDomain = self.cell_clock.get(id(oCell))
            return oDomain.group if oDomain is not None else None

        def add(tNode, oCell, lNets):
            sGroup = dDomain.get(tNode)
            lNodes = dDependencies.setdefault(tNode, [])
            for oNet in lNets:
                for tSource in self.point_nodes(self.sources(oNet)):
                    oSource = dCells.get(tSource) or self._node_cell.get(tSource)
                    sSourceGroup = group(oSource) if oSource is not None else None
                    if sGroup is None or sSourceGroup is None or sSourceGroup == sGroup:
                        lNodes.append(tSource)

        self._node_cell = {}
        dMemories = {}
        for oCell in self.flat.cells:
            if is_register(oCell):
                for iIndex in range(len(oCell.connections.get("Q", []))):
                    self._node_cell[("r", id(oCell), iIndex)] = oCell
            elif oCell.type in MEMORY_READ_TYPES:
                self._node_cell[("d", id(oCell))] = oCell
            elif oCell.is_black_box():
                for sPort in oCell.connections:
                    self._node_cell[("b", id(oCell), sPort.lower())] = oCell
        dInputs = {}
        dResetFanout = {}
        for oCell in self.flat.cells:
            if is_register(oCell) and self.cell_clock.get(id(oCell)) is not None:
                for iIndex in range(len(oCell.connections.get("Q", []))):
                    lData, lReset = self.split_inputs(oCell, iIndex)
                    for sPort, lBits in oCell.connections.items():
                        if sPort in CONTROL_PORTS or sPort in ("Q", "D") or self.flat.direction(oCell, sPort) != "input":
                            continue
                        # An input other than the data input, such as an enable, feeds every bit
                        lData += [b for b in lBits if graph.is_variable(b)]
                    dInputs[("r", id(oCell), iIndex)] = (oCell, lData, lReset)
                    for oNet in lReset:
                        for tSource in self.point_nodes(self.sources(oNet)):
                            dResetFanout.setdefault(tSource, set()).add(id(oCell))
        setResets = set() if bFollowResets else {t for t, s in dResetFanout.items() if len(s) >= 2}
        for tNode, (oCell, lData, lReset) in dInputs.items():
            dCells[tNode] = oCell
            dDomain[tNode] = group(oCell)
            add(tNode, oCell, lData)
            lBefore = list(dDependencies[tNode])
            add(tNode, oCell, lReset)
            dDependencies[tNode] = lBefore + [t for t in dDependencies[tNode][len(lBefore) :] if t not in setResets]
        for oCell in self.flat.cells:
            if oCell.type in ("$memwr", "$memwr_v2", "$meminit", "$meminit_v2"):
                tNode = ("m", oCell.path, str(oCell.cell.get("parameters", {}).get("MEMID")))
                dCells.setdefault(tNode, oCell)
                dDomain.setdefault(tNode, group(oCell) if is_clocked(oCell) else None)
                dMemories.setdefault(tNode, []).append(oCell)
                add(tNode, oCell, self.input_nets(oCell))
        for oCell in self.flat.cells:
            if oCell.type in MEMORY_READ_TYPES:
                tNode = ("d", id(oCell))
                dDomain[tNode] = group(oCell) if is_clocked(oCell) else None
                add(tNode, oCell, self.input_nets(oCell))
                tMemory = ("m", oCell.path, str(oCell.cell.get("parameters", {}).get("MEMID")))
                if tMemory in dDependencies:
                    dDependencies[tNode].append(tMemory)
        return dDependencies, {"cells": dCells}

    @staticmethod
    def _propagate_tags(dDependencies, dSeeds):
        """Returns {node: tag mask}: its own tags and those of every node it depends on, to a fixed point."""
        dSuccessors = {}
        for tNode, lDependencies in dDependencies.items():
            for tDependency in lDependencies:
                dSuccessors.setdefault(tDependency, []).append(tNode)
        dTags = dict(dSeeds)
        lWork = list(dDependencies)
        setQueued = set(lWork)
        while lWork:
            tNode = lWork.pop()
            setQueued.discard(tNode)
            iTags = dSeeds.get(tNode, 0)
            for tDependency in dDependencies.get(tNode, ()):
                iTags |= dTags.get(tDependency, 0)
            if iTags != dTags.get(tNode, 0):
                dTags[tNode] = iTags
                for tNext in dSuccessors.get(tNode, ()):
                    if tNext not in setQueued:
                        setQueued.add(tNext)
                        lWork.append(tNext)
        return dTags

    def gray_coded(self, oCell):
        """Returns whether a register is loaded with the gray code of a binary value: bit i is b(i) xor b(i+1), the top bit b(n)."""
        lPairs = []
        lQ = oCell.connections.get("Q", [])
        for iIndex in range(len(lQ)):
            oNet, _, _ = self.strip(oCell, iIndex)
            tDriver = self.flat.driver(oNet) if graph.is_variable(oNet) else None
            # A register that copies another one, such as the input register of a synchronizer: look at the original
            for _ in range(4):
                if tDriver is None or not is_register(tDriver[0]):
                    break
                oNet, _, _ = self.strip(tDriver[0], tDriver[2])
                tDriver = self.flat.driver(oNet) if graph.is_variable(oNet) else None
            if tDriver is not None and tDriver[0] is not None and tDriver[0].type in ("$xor", "$xnor"):
                oXor, _, iOut = tDriver
                lInputs = [graph.extend(oXor.connections.get("A", []), iOut, False), graph.extend(oXor.connections.get("B", []), iOut, False)]
                lPairs.append({b for b in lInputs if graph.is_variable(b)})
            else:
                lPairs.append({oNet})
        if len(lPairs) < 2:
            return False
        for iIndex in range(len(lPairs) - 1):
            if not lPairs[iIndex] & lPairs[iIndex + 1]:
                return False
        # Only the top bit may be a plain copy; every other bit must be an exclusive or
        return all(len(s) == 2 for s in lPairs[:-1])

    # Resets

    def reset_source(self, oCell):
        """Returns (port, net) of the asynchronous reset of a register, or None."""
        for sPort in RESET_PORTS:
            lNets = oCell.connections.get(sPort, [])
            if lNets and graph.is_variable(lNets[0]):
                return sPort, lNets[0]
        return None

    def reset_root(self, oNet):
        oRoot, _ = self.through_transparent(oNet)
        return oRoot

    def chain_position(self, oCell, iIndex, dMemo):
        """
        The position of a register bit in a reset synchronizer: 1 for a bit with an asynchronous reset that loads a
        constant, n+1 for one that loads from bits at position n or more, directly or through logic such as an and
        of all of them, with the same reset and clock; 0 for any other bit.
        """
        tKey = (id(oCell), iIndex)
        if tKey in dMemo:
            return dMemo[tKey]
        dMemo[tKey] = 0
        tReset = self.reset_source(oCell)
        if tReset is None:
            return 0
        oRoot = self.reset_root(tReset[1])
        oDomain = self.cell_clock.get(id(oCell))
        oNet, _, _ = self.strip(oCell, iIndex)
        if not graph.is_variable(oNet) or self.constant_choice(oNet):
            dMemo[tKey] = 1
            return 1
        lPositions = []
        for oSource, sPort, iSource in self.sources(oNet):
            if not is_register(oSource) or sPort != "Q" or self.cell_clock.get(id(oSource)) is not oDomain:
                return 0
            tSourceReset = self.reset_source(oSource)
            if tSourceReset is None or self.reset_root(tSourceReset[1]) != oRoot:
                return 0
            lPositions.append(self.chain_position(oSource, iSource, dMemo))
        if not lPositions or min(lPositions) == 0:
            return 0
        dMemo[tKey] = max(lPositions) + 1
        return dMemo[tKey]

    def constant_choice(self, oNet):
        """Returns whether a net is a multiplexer of constants, such as a synchronous reset that loads 0 or 1."""
        tDriver = self.flat.driver(oNet)
        if tDriver is None or tDriver[0] is None or tDriver[0].type not in MUX_TYPES:
            return False
        oMux = tDriver[0]
        iWidth = max(len(oMux.connections.get("Y", [])), 1)
        lData = [graph.extend(oMux.connections.get("A", []), tDriver[2], False)] + oMux.connections.get("B", [])[tDriver[2] :: iWidth]
        return all(not graph.is_variable(b) for b in lData)

    def is_reset_synchronizer(self, oCell, dMemo):
        """Returns whether every bit of a register is part of a reset synchronizer: at a position, in a chain of two or more."""
        lQ = oCell.connections.get("Q", [])
        lPositions = [self.chain_position(oCell, i, dMemo) for i in range(len(lQ))]
        if not lPositions or min(lPositions) == 0:
            return False
        if max(lPositions) >= 2:
            return True
        # A first stage: some register continues the chain
        return any(self.chain_position(t[0], t[2], dMemo) >= 2 for b in lQ for t in self.flat.readers.get(b, []) if is_register(t[0]) and t[1] == "D")

    def is_reset_synchronizer_output(self, oNet, dMemo):
        """Returns whether a net is a reset synchronizer bit at position 2 or more."""
        tDriver = self.flat.driver(oNet)
        if tDriver is None or not is_register(tDriver[0]):
            return False
        return self.chain_position(tDriver[0], tDriver[2], dMemo) >= 2

    def _find_resets(self):
        lRegisters = [o for o in self.flat.cells if is_register(o) and self.reset_source(o) is not None]
        dGroups = {}
        dMemo = {}
        for oCell in lRegisters:
            oRoot = self.reset_root(self.reset_source(oCell)[1])
            dGroups.setdefault(oRoot, []).append(oCell)
        dInputs = {str(k).lower(): str(v).lower() for k, v in (self.constraints.get("inputs") or {}).items()}
        dFindings = {}
        for oRoot, lCells in dGroups.items():
            if not graph.is_variable(oRoot):
                continue
            tDriver = self.flat.driver(oRoot)
            sName = self.flat.net_name(oRoot)
            for oCell in lCells:
                oDomain = self.cell_clock.get(id(oCell))
                if oDomain is None:
                    continue
                # The registers of a reset synchronizer take a reset from anywhere: they release it synchronously
                if self.is_reset_synchronizer(oCell, dMemo):
                    continue
                if tDriver is None or tDriver[0] is None:
                    sDomain = dInputs.get(sName.lower())
                    if sDomain is not None and sDomain != "async" and any(o.name.lower() == sDomain and o.group == oDomain.group for o in self.clocks.values()):
                        continue
                    tKey = ("raw", oRoot, oDomain.group)
                elif tDriver[0].is_black_box():
                    # A declared output: released asynchronously, or synchronously to one of the box's clocks
                    oSourceDomain = self.box_domain(tDriver[0], tDriver[1])
                    if oSourceDomain is None:
                        continue
                    if oSourceDomain == "async":
                        tKey = ("raw", oRoot, oDomain.group)
                    elif oSourceDomain.group != oDomain.group:
                        tKey = ("crossing", oRoot, oDomain.group)
                    else:
                        continue
                elif self.is_reset_synchronizer_output(oRoot, dMemo):
                    oSourceDomain = self.cell_clock.get(id(tDriver[0]))
                    if oSourceDomain is not None and oSourceDomain.group == oDomain.group:
                        continue
                    tKey = ("crossing", oRoot, oDomain.group)
                else:
                    tKey = ("generated", oRoot, None)
                dFindings.setdefault(tKey, []).append(oCell)
        for (sKind, oRoot, _), lCells in dFindings.items():
            tDriver = self.flat.driver(oRoot)
            oCell = tDriver[0] if tDriver is not None and tDriver[0] is not None else lCells[0]
            oDomain = self.cell_clock.get(id(lCells[0]))
            if sKind == "crossing":
                if tDriver[0].is_black_box():
                    oSourceDomain = self.box_domain(tDriver[0], tDriver[1])
                else:
                    oSourceDomain = self.cell_clock.get(id(tDriver[0]))
                sDetail = f"synchronized to {oSourceDomain.name}, resets registers clocked by {oDomain.name}"
            elif sKind == "raw":
                sDetail = f"resets registers clocked by {oDomain.name}"
            else:
                sDetail = "made by " + ("a register" if tDriver is not None and is_register(tDriver[0]) else "logic")
            sReset = self.flat.net_name(oRoot)
            if sReset.startswith("net ") and tDriver is not None and tDriver[0] is not None:
                # A reset made by logic has no name of its own: name it after its inputs
                sReset = "logic of " + ", ".join(sorted({self.point_name(t) for t in self.sources(oRoot)}))
            self.resets.append(ResetFinding(sKind, oCell, sReset, lCells, sDetail))
        # A net that is both a clock and an asynchronous reset
        dClockRoots = {o.net: o for o in self.clocks.values() if o.kind in ("port", "box", "register", "logic")}
        for oRoot, lCells in dGroups.items():
            if oRoot in dClockRoots:
                self.shared.append((dClockRoots[oRoot], lCells))

    # Clocks used as data

    def _find_clock_as_data(self):
        """Readers of a clock from a port or a black box that are neither clock pins nor logic that makes a clock."""
        setClockNets = set()
        for oCell in self.flat.cells:
            if is_clocked(oCell) and "CLK" in oCell.connections:
                oNet = oCell.connections["CLK"][0]
                while graph.is_variable(oNet) and oNet not in setClockNets:
                    setClockNets.add(oNet)
                    tDriver = self.flat.driver(oNet)
                    if tDriver is None or tDriver[0] is None or tDriver[0].is_black_box() or is_clocked(tDriver[0]):
                        break
                    if tDriver[0].type in TRANSPARENT_TYPES:
                        oNet = graph.extend(tDriver[0].connections.get("A", []), tDriver[2], False)
                    else:
                        # A gate on the clock: its inputs are part of the clock network
                        for oInput in self.comb_inputs(*tDriver):
                            setClockNets.add(oInput)
                        break
        dReaders = {}
        for oDomain in self.clocks.values():
            if oDomain.kind not in ("port", "box"):
                continue
            lWork = [oDomain.net]
            setSeen = set()
            while lWork:
                oNet = lWork.pop()
                if oNet in setSeen:
                    continue
                setSeen.add(oNet)
                for oCell, sPort, _ in self.flat.readers.get(oNet, []):
                    if oCell is None:
                        continue
                    if oCell.is_black_box():
                        oInstance = self.boxes.get(id(oCell))
                        oRole = oInstance.role(sPort) if oInstance is not None else None
                        # A clock through a declared buffer is still a clock; reaching a data input it is data
                        for sOutput, lOutputs in oCell.connections.items():
                            oOutputRole = oInstance.role(sOutput) if oInstance is not None else None
                            if oOutputRole is not None and (
                                (oOutputRole.kind == "clock_out" and oOutputRole.relation == "same" and (oOutputRole.source or "").lower() == sPort.lower())
                                or (oOutputRole.kind == "path" and sPort.lower() in [s.lower() for s in oOutputRole.inputs])
                            ):
                                lWork.extend(b for b in lOutputs if graph.is_variable(b))
                        if oRole is not None and oRole.kind in ("sync", "async", "static"):
                            dReaders.setdefault((oDomain.key, oCell.module, oCell.name), (oDomain, oCell))
                        continue
                    # A clock pin, or an asynchronous reset, which is a shared clock and reset
                    if (sPort == "CLK" and is_clocked(oCell)) or sPort in RESET_PORTS:
                        continue
                    lOutputs = [b for s, l in oCell.connections.items() if self.flat.direction(oCell, s) == "output" for b in l if graph.is_variable(b)]
                    if oCell.type in TRANSPARENT_TYPES:
                        lWork.extend(lOutputs)
                        continue
                    if any(b in setClockNets for b in lOutputs):
                        continue
                    dReaders.setdefault((oDomain.key, oCell.module, oCell.name), (oDomain, oCell))
        self.clock_as_data = list(dReaders.values())

    # Waivers

    def _apply_waivers(self):
        for dWaiver in self.constraints.get("waivers") or []:
            sSignal = str(dWaiver.get("signal", ""))
            sJustification = str(dWaiver.get("justification") or "").strip()
            if not sJustification:
                self.waiver_errors.append(sSignal)
                continue
            for oCrossing in self.crossings:
                if oCrossing.status not in SAFE and (oCrossing.name == sSignal or fnmatch.fnmatchcase(oCrossing.name, sSignal)):
                    oCrossing.justification = sJustification
                    oCrossing.original_status = oCrossing.status
                    oCrossing.status = WAIVED

    # Report

    def box_report(self):
        """The black box part of the report: declarations, internal synchronizers for review, static ports, problems."""
        dTypes = {}
        for oInstance in self.boxes.values():
            dTypes.setdefault(oInstance.cell.type, []).append(oInstance)
        lTypes = []
        lStatic = []
        for sType, lInstances in sorted(dTypes.items(), key=lambda t: t[0].lower()):
            oFirst = lInstances[0]
            lTypes.append(
                {
                    "type": sType,
                    "instances": len(lInstances),
                    "declared": all(o.declared() for o in lInstances),
                    "declared_in": sorted({d.source for o in lInstances for d in o.declarations}),
                    "reference": oFirst.reference(),
                    "reviewed_by": oFirst.reviewed_by(),
                },
            )
            for oInstance in lInstances:
                for sPort in sorted(oInstance.cell.connections):
                    oRole = oInstance.role(sPort)
                    if oRole is not None and oRole.kind == "static":
                        lStatic.append(
                            {"port": f"{oInstance.cell!r}.{sPort}", "justification": oRole.justification, "reviewed_by": oInstance.reviewed_by(oRole)},
                        )
        lSynchronizers = []
        for oInstance, sPort, oRole, oSource, oDestination in self.box_synchronizers:
            if sPort is None:
                lSynchronizers.append({"instance": repr(oInstance.cell), "type": oInstance.cell.type, "kind": "dual clock FIFO"})
                continue
            lSynchronizers.append(
                {
                    "instance": repr(oInstance.cell),
                    "type": oInstance.cell.type,
                    "kind": "synchronizer",
                    "output": sPort,
                    "input": oRole.source,
                    "from": oSource.name if isinstance(oSource, Clock) else oSource,
                    "clock": oDestination.name if oDestination is not None else None,
                    "stages": oInstance.stages(oRole),
                },
            )
        return {
            "black_boxes": lTypes,
            "box_synchronizers": lSynchronizers,
            "static_ports": lStatic,
            "box_problems": [s for _, s, _ in self.box_problems],
        }

    def cell_location(self, oCell, sSignal=None):
        oLocation = self.flat.location(oCell)
        return (oLocation.file, oLocation.line) if oLocation else (None, 0)

    def report(self):
        """Returns the crossing report as a dictionary."""
        dReturn = {"top": netlist.module_name(self.flat.top), "clocks": [], "crossings": [], "resets": []}
        for oDomain in sorted(self.clocks.values(), key=lambda o: o.name):
            if oDomain.registers == 0 and oDomain.kind != "logic":
                continue
            dReturn["clocks"].append(
                {
                    "name": oDomain.name,
                    "kind": oDomain.kind,
                    "source": oDomain.key,
                    "group": self.clocks[oDomain.group].name if oDomain.group in self.clocks else oDomain.group,
                    "registers": oDomain.registers,
                    "from": oDomain.parent.name if oDomain.parent else None,
                },
            )
        for oCrossing in self.crossings:
            sFile, iLine = self.locate(oCrossing.cell, oCrossing.name.split(".")[-1])
            dReturn["crossings"].append(
                {
                    "destination": oCrossing.name,
                    "clock": oCrossing.clock.name,
                    "sources": [{"signal": s, "clock": o.name} for s, o in sorted(oCrossing.sources.items())],
                    "status": oCrossing.status,
                    "detail": oCrossing.detail,
                    "stages": oCrossing.stages,
                    "justification": oCrossing.justification,
                    "location": f"{sFile}:{iLine}" if sFile else None,
                },
            )
        dReturn["reconvergences"] = []
        for lEndpoints, lSignals in self.reconvergences:
            sFile, iLine = self.reconvergence_location(lEndpoints[0])
            dReturn["reconvergences"].append(
                {
                    "synchronizers": [{"signal": t[0], "synchronizer": t[1], "clock": t[2].name if t[2] != "async" else "async"} for t in lSignals],
                    "clock": self.endpoint_clock(lEndpoints[0]),
                    "points": [self.endpoint_name(o) for o in lEndpoints],
                    "location": f"{sFile}:{iLine}" if sFile else None,
                },
            )
        dReturn["reconvergences_through_resets"] = []
        for lEndpoints, lSignals in self.reset_reconvergences:
            sFile, iLine = self.reconvergence_location(lEndpoints[0])
            dReturn["reconvergences_through_resets"].append(
                {
                    "synchronizers": [{"signal": t[0], "synchronizer": t[1], "clock": t[2].name if t[2] != "async" else "async"} for t in lSignals],
                    "clock": self.endpoint_clock(lEndpoints[0]),
                    "points": [self.endpoint_name(o) for o in lEndpoints],
                    "location": f"{sFile}:{iLine}" if sFile else None,
                },
            )
        dReturn.update(self.box_report())
        for oReset in self.resets:
            dReturn["resets"].append({"reset": oReset.reset, "kind": oReset.kind, "detail": oReset.detail, "registers": len(oReset.cells)})
        return dReturn


def new_meetings(lSets, lTags):
    """
    Returns the mask of the tags that meet for the first time where inputs with the tag masks lSets come together:
    pairs of tags of the same source and destination domains that no single input carries already.
    """
    iUnion = 0
    for iSet in lSets:
        iUnion |= iSet
    if bin(iUnion).count("1") < 2:
        return 0
    dGroups = {}
    for iTag in range(len(lTags)):
        if iUnion >> iTag & 1:
            dGroups.setdefault(lTags[iTag][3], []).append(iTag)
    iReturn = 0
    for lMembers in dGroups.values():
        if len(lMembers) < 2:
            continue
        iMask = sum(1 << i for i in lMembers)
        if any(iSet & iMask == iMask for iSet in lSets):
            continue
        lSets_ = [iSet & iMask for iSet in lSets if iSet & iMask]
        for iFirst, iA in enumerate(lMembers):
            for iB in lMembers[iFirst + 1 :]:
                iPair = (1 << iA) | (1 << iB)
                if not any(iSet & iPair == iPair for iSet in lSets_):
                    iReturn |= iPair
    return iReturn


def report_text(dReport):
    """Returns the crossing report as text."""
    lLines = [f"Clock domain crossing report for {dReport['top']}", "", "Clocks"]
    for dClock in dReport["clocks"]:
        sFrom = f", from {dClock['from']}" if dClock["from"] else ""
        lLines.append(
            f"  {dClock['name']}: {dClock['kind']} {dClock['source'].split(' ', 1)[-1]}, group {dClock['group']}, {'1 register' if dClock['registers'] == 1 else str(dClock['registers']) + ' registers'}{sFrom}",
        )
    lLines += ["", "Crossings"]
    if not dReport["crossings"]:
        lLines.append("  none")
    for dCrossing in dReport["crossings"]:
        sSources = ", ".join(f"{d['signal']} ({d['clock']})" for d in dCrossing["sources"])
        lLines.append(f"  {dCrossing['destination']} ({dCrossing['clock']}) <- {sSources}")
        lLines.append(f"    {dCrossing['status']}" + (f": {dCrossing['detail']}" if dCrossing["detail"] else ""))
        if dCrossing["justification"]:
            lLines.append(f"    justification: {dCrossing['justification']}")
        if dCrossing["location"]:
            lLines.append(f"    at {dCrossing['location']}")
    lLines += ["", "Reconvergence"]
    if not dReport.get("reconvergences"):
        lLines.append("  none")
    for dReconvergence in dReport.get("reconvergences", []):
        sSignals = ", ".join(f"{d['signal']} ({d['clock']}, by {d['synchronizer']})" for d in dReconvergence["synchronizers"])
        sClock = f" ({dReconvergence['clock']})" if dReconvergence["clock"] else ""
        lLines.append(f"  {sSignals} meet in {', '.join(dReconvergence['points'])}{sClock}")
        if dReconvergence["location"]:
            lLines.append(f"    at {dReconvergence['location']}")
    if dReport.get("reconvergences_through_resets"):
        lLines += ["", "Reconvergence through synchronous resets (reported by design_016 with follow_resets)"]
        for dReconvergence in dReport["reconvergences_through_resets"]:
            sSignals = ", ".join(f"{d['signal']} ({d['clock']}, by {d['synchronizer']})" for d in dReconvergence["synchronizers"])
            sClock = f" ({dReconvergence['clock']})" if dReconvergence["clock"] else ""
            lLines.append(f"  {sSignals} meet in {', '.join(dReconvergence['points'])}{sClock}")
            if dReconvergence["location"]:
                lLines.append(f"    at {dReconvergence['location']}")
    if dReport.get("black_boxes"):
        lLines += ["", "Black boxes"]
        for dType in dReport["black_boxes"]:
            sState = "declared in " + ", ".join(dType["declared_in"]) if dType["declared"] else "NOT DECLARED"
            sReference = f", reference {dType['reference']}" if dType["reference"] else ""
            sReviewed = f", reviewed by {dType['reviewed_by']}" if dType["reviewed_by"] else ""
            sInstances = "1 instance" if dType["instances"] == 1 else f"{dType['instances']} instances"
            lLines.append(f"  {dType['type']}: {sInstances}, {sState}{sReference}{sReviewed}")
    if dReport.get("box_problems"):
        lLines += ["", "Black box problems"]
        for sProblem in dReport["box_problems"]:
            lLines.append(f"  {sProblem}")
    if dReport.get("box_synchronizers"):
        lLines += ["", "Synchronized inside black boxes (manual review)"]
        for dSynchronizer in dReport["box_synchronizers"]:
            if dSynchronizer["kind"] != "synchronizer":
                lLines.append(f"  {dSynchronizer['instance']} ({dSynchronizer['type']}): {dSynchronizer['kind']}")
                continue
            sStages = f", {dSynchronizer['stages']} stages" if dSynchronizer["stages"] is not None else ", stages not known"
            sFrom = f" from {dSynchronizer['from']}" if dSynchronizer["from"] else ""
            lLines.append(
                f"  {dSynchronizer['instance']}.{dSynchronizer['output']} ({dSynchronizer['type']}): {dSynchronizer['input']}{sFrom} to {dSynchronizer['clock']}{sStages}",
            )
    if dReport.get("static_ports"):
        lLines += ["", "Static black box ports"]
        for dStatic in dReport["static_ports"]:
            lLines.append(f"  {dStatic['port']}: {dStatic['justification']} (reviewed by {dStatic['reviewed_by'] or 'nobody'})")
    lLines += ["", "Reset findings"]
    if not dReport["resets"]:
        lLines.append("  none")
    for dReset in dReport["resets"]:
        lLines.append(f"  {dReset['reset']}: {dReset['kind']}, {dReset['detail']}, {dReset['registers']} registers")
    lCounts = {}
    for dCrossing in dReport["crossings"]:
        lCounts[dCrossing["status"]] = lCounts.get(dCrossing["status"], 0) + 1
    lLines += ["", "Summary: " + (", ".join(f"{v} {k}" for k, v in sorted(lCounts.items())) or "no crossings")]
    return "\n".join(lLines) + "\n"
