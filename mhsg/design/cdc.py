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

from mhsg.design import graph, netlist

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
    def __init__(self, oFlat, dConstraints=None, fLocate=None):
        self.flat = oFlat
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
        self._find_clocks()
        self._find_crossings()
        self._find_resets()
        self._find_clock_as_data()
        self._apply_waivers()

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
            if oCell is None or oCell.is_black_box() or is_clocked(oCell) or oCell.type in MEMORY_READ_TYPES or oCell.type in graph.STATE_TYPES:
                self._dSources[oCurrent] = frozenset([tDriver])
                continue
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
            return self.clock("box " + sName, "box", sName, oRoot, oCell)
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
            return None
        return self.cell_clock.get(id(oCell))

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
        self._find_buses()
        self.crossings.sort(key=lambda o: o.name)
        self._find_reconvergence()

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

    def _find_reconvergence(self):
        """
        Signals synchronized separately from one clock domain can change in different cycles of the destination clock,
        so logic that combines them can see a state the source never had. A register whose inputs depend on two or
        more of them, through logic of its own domain, is a reconvergence. The bits of one bus count as one signal:
        a gray-coded bus is meant to be combined, and a bus synchronized bit by bit is reported as a hazard already.
        """
        dOutputs = {}
        for oCrossing in self.crossings:
            if oCrossing.status not in (SYNCHRONIZED, GRAY, BUS) and getattr(oCrossing, "original_status", None) not in (SYNCHRONIZED, GRAY, BUS):
                continue
            for iIndex, tSource in getattr(oCrossing, "first_stages", []):
                _, oLast, iLast = self.chain(oCrossing.cell, iIndex)
                oSourceDomain = self.domain_of(tSource)
                if oSourceDomain is None:
                    continue
                sSourceGroup = "async" if oSourceDomain == "async" else oSourceDomain.group
                if oCrossing.status in (GRAY, BUS) or getattr(oCrossing, "original_status", None) in (GRAY, BUS):
                    tKey = ("bus", id(tSource[0]))
                    sName = self.flat.cell_name(tSource[0])
                else:
                    tKey = ("bit", id(tSource[0]), tSource[2])
                    sName = self.point_name(tSource)
                    if len(tSource[0].connections.get("Q", [])) > 1:
                        sName += f"({tSource[2]})"
                dOutputs[oLast.connections["Q"][iLast]] = (tKey, sName, sSourceGroup, oCrossing.clock.group, oSourceDomain)
        if len(dOutputs) < 2:
            return
        dFound = {}
        for oCell in self.flat.cells:
            oDomain = self.cell_clock.get(id(oCell))
            if not is_register(oCell) or oDomain is None:
                continue
            dSignals = {}
            for sPort, lNets in oCell.connections.items():
                if sPort in CONTROL_PORTS or sPort == "Q" or self.flat.direction(oCell, sPort) != "input":
                    continue
                for oNet in lNets:
                    if not graph.is_variable(oNet):
                        continue
                    for oSource, sSourcePort, iSource in self.sources(oNet):
                        if oSource is None or sSourcePort != "Q":
                            continue
                        tOutput = dOutputs.get(oSource.connections["Q"][iSource])
                        if tOutput is None or tOutput[3] != oDomain.group:
                            continue
                        dSignals.setdefault(tOutput[2], {})[tOutput[0]] = (tOutput[1], tOutput[4])
            for sGroup, dKeys in dSignals.items():
                if len(dKeys) < 2:
                    continue
                tKey = (sGroup, frozenset(dKeys))
                dFound.setdefault(tKey, (sorted(dKeys.values(), key=lambda t: t[0]), []))[1].append(oCell)
        for lSignals, lCells in dFound.values():
            lCells.sort(key=self.flat.cell_name)
            self.reconvergences.append((lCells, lSignals))
        self.reconvergences.sort(key=lambda t: self.flat.cell_name(t[0][0]))

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
                    if oCell is None or oCell.is_black_box():
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
        for lCells, lSignals in self.reconvergences:
            sFile, iLine = self.locate(lCells[0], self.flat.cell_name(lCells[0]).split(".")[-1])
            dReturn["reconvergences"].append(
                {
                    "signals": [{"signal": s, "clock": o.name if o != "async" else "async"} for s, o in lSignals],
                    "clock": self.cell_clock[id(lCells[0])].name,
                    "registers": [self.flat.cell_name(o) for o in lCells],
                    "location": f"{sFile}:{iLine}" if sFile else None,
                },
            )
        for oReset in self.resets:
            dReturn["resets"].append({"reset": oReset.reset, "kind": oReset.kind, "detail": oReset.detail, "registers": len(oReset.cells)})
        return dReturn


def report_text(dReport):
    """Returns the crossing report as text."""
    lLines = [f"Clock domain crossing report for {dReport['top']}", "", "Clocks"]
    for dClock in dReport["clocks"]:
        sFrom = f", from {dClock['from']}" if dClock["from"] else ""
        lLines.append(
            f"  {dClock['name']}: {dClock['kind']} {dClock['source'].split(' ', 1)[-1]}, group {dClock['group']}, {dClock['registers']} registers{sFrom}",
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
        sSignals = ", ".join(f"{d['signal']} ({d['clock']})" for d in dReconvergence["signals"])
        lLines.append(f"  {sSignals} meet in {', '.join(dReconvergence['registers'])} ({dReconvergence['clock']})")
        if dReconvergence["location"]:
            lLines.append(f"    at {dReconvergence['location']}")
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
