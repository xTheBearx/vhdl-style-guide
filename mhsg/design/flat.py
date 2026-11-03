# -*- coding: utf-8 -*-
"""
A flat view of a hierarchical Yosys netlist, built in Python, for the analyses that follow signals across the
hierarchy, such as clock domain crossings.

Every instance of a module in the netlist is replaced by its cells, and every net gets one global number. Each flat
cell keeps the module it comes from and its name there, so its source location and the names of its nets can be
found as in the hierarchical netlist. Cells whose type is not a module of the netlist are kept as black boxes.
"""

from mhsg.design import graph


class Cell:
    """A cell of the flat netlist."""

    def __init__(self, tPath, sModule, sName, dCell, dConnections, dLocal):
        # The instance names from the top down to the module that holds the cell
        self.path = tPath
        self.module = sModule
        self.name = sName
        self.cell = dCell
        self.type = dCell.get("type", "")
        # port -> list of global net numbers, or constants such as "0"
        self.connections = dConnections
        # port -> list of the net numbers in the module
        self.local = dLocal

    def is_black_box(self):
        return not self.type.startswith("$")

    def parameter(self, sName, iDefault=0):
        return graph.parameter(self.cell, sName, iDefault)

    def __repr__(self):
        return ".".join(self.path + (self.name,))


class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, iItem):
        lPath = []
        while self.parent.get(iItem, iItem) != iItem:
            lPath.append(iItem)
            iItem = self.parent[iItem]
        for iMember in lPath:
            self.parent[iMember] = iItem
        return iItem

    def union(self, iFirst, iSecond):
        iFirst = self.find(iFirst)
        iSecond = self.find(iSecond)
        if iFirst != iSecond:
            self.parent[iSecond] = iFirst


class FlatDesign:
    """The flattened top module of a netlist."""

    def __init__(self, oNetlist, sTop=None):
        self.netlist = oNetlist
        self.top = sTop or top_module(oNetlist)
        self.cells = []
        # global net -> list of (cell, port, index); top ports are (None, port, index)
        self.drivers = {}
        self.readers = {}
        # global net -> (path, module, local net), the first place the net was seen, for its name
        self.origin = {}
        self._oUnion = UnionFind()
        self._iNext = 0
        self._flatten()

    # Building

    def _new_net(self):
        self._iNext += 1
        return self._iNext

    def _flatten(self):
        lCells = []
        dTop = self.netlist.modules.get(self.top, {})
        dTopNets = {}
        for sPort, dPort in dTop.get("ports", {}).items():
            for oBit in dPort.get("bits", []):
                if graph.is_variable(oBit) and oBit not in dTopNets:
                    dTopNets[oBit] = self._new_net()
        lWork = [((), self.top, dTopNets)]
        while lWork:
            tPath, sModule, dBinding = lWork.pop()
            dModule = self.netlist.modules[sModule]

            def net(oBit, dBinding=dBinding, tPath=tPath, sModule=sModule):
                if not graph.is_variable(oBit):
                    return oBit
                if oBit not in dBinding:
                    dBinding[oBit] = self._new_net()
                oValue = dBinding[oBit]
                if graph.is_variable(oValue):
                    self.origin.setdefault(oValue, (tPath, sModule, oBit))
                return oValue

            for sName, dNet in dModule.get("netnames", {}).items():
                if not dNet.get("hide_name"):
                    for oBit in dNet.get("bits", []):
                        net(oBit)
            for sName, dCell in dModule.get("cells", {}).items():
                sType = dCell.get("type", "")
                dConnections = dCell.get("connections", {})
                if sType in self.netlist.modules:
                    # An instance: bind the ports of the module to the nets connected to them
                    dChild = {}
                    for sPort, dPort in self.netlist.modules[sType].get("ports", {}).items():
                        for iIndex, oChildBit in enumerate(dPort.get("bits", [])):
                            lParent = dConnections.get(sPort, [])
                            oValue = net(lParent[iIndex]) if iIndex < len(lParent) else "x"
                            if not graph.is_variable(oChildBit):
                                continue
                            if oChildBit in dChild and graph.is_variable(dChild[oChildBit]) and graph.is_variable(oValue):
                                self._oUnion.union(dChild[oChildBit], oValue)
                            else:
                                dChild.setdefault(oChildBit, oValue)
                    lWork.append((tPath + (sName.lstrip("\\"),), sType, dChild))
                    continue
                dGlobal = {sPort: [net(b) for b in lBits] for sPort, lBits in dConnections.items()}
                lCells.append(Cell(tPath, sModule, sName, dCell, dGlobal, dConnections))
        # Merge the nets that ports joined, then index drivers and readers
        for oCell in lCells:
            oCell.connections = {s: [self.find(b) for b in l] for s, l in oCell.connections.items()}
            self.cells.append(oCell)
        self.top_ports = {}
        for sPort, dPort in dTop.get("ports", {}).items():
            lNets = [self.find(dTopNets[b]) if graph.is_variable(b) else b for b in dPort.get("bits", [])]
            self.top_ports[sPort] = (dPort.get("direction"), lNets)
            for iIndex, oNet in enumerate(lNets):
                if not graph.is_variable(oNet):
                    continue
                if dPort.get("direction") in ("input", "inout"):
                    self.drivers.setdefault(oNet, []).append((None, sPort, iIndex))
                if dPort.get("direction") in ("output", "inout"):
                    self.readers.setdefault(oNet, []).append((None, sPort, iIndex))
        for oCell in self.cells:
            for sPort, lNets in oCell.connections.items():
                sDirection = self.direction(oCell, sPort)
                for iIndex, oNet in enumerate(lNets):
                    if not graph.is_variable(oNet):
                        continue
                    if sDirection in ("output", "inout"):
                        self.drivers.setdefault(oNet, []).append((oCell, sPort, iIndex))
                    if sDirection in ("input", "inout"):
                        self.readers.setdefault(oNet, []).append((oCell, sPort, iIndex))
        self.origin = {self.find(k): v for k, v in reversed(list(self.origin.items()))}

    def find(self, oNet):
        return self._oUnion.find(oNet) if graph.is_variable(oNet) else oNet

    # Queries

    def direction(self, oCell, sPort):
        sDirection = oCell.cell.get("port_directions", {}).get(sPort)
        if sDirection is None:
            sDirection = "output" if sPort in graph.OUTPUT_PORTS else "input"
        return sDirection

    def driver(self, oNet):
        """Returns (cell, port, index) of the first cell that drives a net, (None, port, index) for a top input, or None."""
        lDrivers = self.drivers.get(oNet, [])
        for tDriver in lDrivers:
            if tDriver[0] is not None:
                return tDriver
        return lDrivers[0] if lDrivers else None

    def input_port(self, oNet):
        """Returns the name of the top input port a net is, or None."""
        for oCell, sPort, iIndex in self.drivers.get(oNet, []):
            if oCell is None:
                return sPort if len(self.top_ports[sPort][1]) == 1 else f"{sPort}({iIndex})"
        return None

    def net_name(self, oNet):
        """Returns the hierarchical name of a net, such as u_sync.reg0, preferring names written in the VHDL."""
        if not graph.is_variable(oNet):
            return str(oNet)
        sPort = self.input_port(oNet)
        if sPort is not None:
            return sPort
        tOrigin = self.origin.get(oNet)
        if tOrigin is None:
            return f"net {oNet}"
        tPath, sModule, iBit = tOrigin
        sName = self.netlist.bit_name(sModule, iBit) or f"net {oNet}"
        return ".".join(tPath + (sName.lstrip("\\"),))

    def cell_name(self, oCell, sPort="Q"):
        """Returns the hierarchical name of the signal a cell drives, such as u_sync.reg0 for a register."""
        lLocal = oCell.local.get(sPort) or []
        lInts = [b for b in lLocal if graph.is_variable(b)]
        if lInts:
            sName = self.netlist.bit_name(oCell.module, lInts[0])
            if sName and not sName.startswith("$"):
                return ".".join(oCell.path + (sName.lstrip("\\"),))
        return repr(oCell)

    def location(self, oCell):
        return self.netlist.location(oCell.module, oCell.name)


def top_module(oNetlist):
    """Returns the module that no other module instantiates; the one with the most cells if there are several."""
    setInstantiated = {d.get("type") for m in oNetlist.modules.values() for d in m.get("cells", {}).values()}
    lRoots = [s for s in oNetlist.modules if s not in setInstantiated]
    if not lRoots:
        return next(iter(oNetlist.modules))
    return max(lRoots, key=lambda s: len(oNetlist.modules[s].get("cells", {})))
