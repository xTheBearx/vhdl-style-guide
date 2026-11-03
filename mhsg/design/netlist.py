# -*- coding: utf-8 -*-
"""
Reads the JSON netlist of Yosys and maps its cells back to VHDL source locations.

The GHDL plugin for Yosys writes no source locations into the netlist. The cells it creates are named after GHDL's
instance numbers, such as \\17, and GHDL's Verilog output names the same instance n17_q or n17_o and writes a comment
with its location before it, such as /* fifo.vhd:42:5 */. Joining the two gives each cell the location of the VHDL
statement it came from, as a single line and column.
"""

import re

LATCH_TYPES = {"$dlatch", "$adlatch", "$dlatchsr"}
MUX_TYPES = {"$mux", "$pmux"}
FLIP_FLOP_TYPES = {"$dff", "$dffe", "$adff", "$adffe", "$sdff", "$sdffe", "$sdffce", "$aldff", "$aldffe", "$dffsr", "$dffsre"}

reLocation = re.compile(r"^\s*/\* (\S+):(\d+):(\d+)\s+\*/")
reModule = re.compile(r"^module (\S+)")
reInstanceOutput = re.compile(r"\bn(\d+)_[a-z]+\b\s*(?:<=|=)")


class Location:
    def __init__(self, sFile, iLine, iColumn):
        self.file = sFile
        self.line = iLine
        self.column = iColumn

    def __repr__(self):
        return f"{self.file}:{self.line}:{self.column}"


def read_locations(sVerilogFile):
    """Returns {(module, instance number): Location} from the location comments of GHDL's Verilog output."""
    dReturn = {}
    sModule = None
    oLocation = None
    with open(sVerilogFile, encoding="utf-8", errors="replace") as oFile:
        for sLine in oFile:
            oMatch = reModule.match(sLine)
            if oMatch:
                sModule, oLocation = oMatch.group(1), None
                continue
            oMatch = reLocation.match(sLine)
            if oMatch:
                oLocation = Location(oMatch.group(1), int(oMatch.group(2)), int(oMatch.group(3)))
                continue
            if oLocation is None or sModule is None:
                continue
            for oInstance in reInstanceOutput.finditer(sLine):
                dReturn.setdefault((sModule, oInstance.group(1)), oLocation)
            if sLine.strip() == "" or sLine.startswith("endmodule"):
                oLocation = None
    return dReturn


class Netlist:
    """The modules of a Yosys JSON netlist, with the location of each cell and the names of its nets."""

    def __init__(self, dNetlist, dLocations):
        self.modules = dNetlist.get("modules", {})
        self.locations = dLocations

    def cells(self, lTypes=None):
        """Yields (module name, cell name, cell) for every cell, or for the cells of the given types."""
        for sModule, dModule in self.modules.items():
            for sCell, dCell in dModule.get("cells", {}).items():
                if lTypes is None or dCell.get("type") in lTypes:
                    yield sModule, sCell, dCell

    def latches(self):
        """
        Yields (module name, cell name, cell) for each latch: a latch cell, or a multiplexer whose output feeds
        back to one of its data inputs, which is how the GHDL plugin builds some latches.
        """
        for sModule, sCell, dCell in self.cells():
            sType = dCell.get("type")
            if sType in LATCH_TYPES:
                yield sModule, sCell, dCell
            elif sType in MUX_TYPES:
                dConnections = dCell.get("connections", {})
                setOutputs = {b for b in dConnections.get("Y", []) if isinstance(b, int)}
                setInputs = {b for sPort in ("A", "B") for b in dConnections.get(sPort, []) if isinstance(b, int)}
                if setOutputs & setInputs:
                    yield sModule, sCell, dCell

    def location(self, sModule, sCell):
        """Returns the Location of a cell, or None if it is not known."""
        return self.locations.get((module_name(sModule), sCell.lstrip("\\").split(".")[-1]))

    def bit_name(self, sModule, iBit):
        """Returns the name of the signal or port a bit belongs to, preferring names written in the VHDL."""
        dModule = self.modules.get(sModule, {})
        sReturn = None
        for sName, dPort in dModule.get("ports", {}).items():
            if iBit in dPort.get("bits", []):
                return sName
        for sName, dNet in dModule.get("netnames", {}).items():
            if iBit in dNet.get("bits", []) and not dNet.get("hide_name"):
                if sReturn is None or (sReturn.startswith("$") and not sName.startswith("$")):
                    sReturn = sName
        return sReturn


def module_name(sModule):
    """Returns a module name as GHDL writes it in Verilog: without the backslash Yosys adds."""
    return sModule.lstrip("\\")
