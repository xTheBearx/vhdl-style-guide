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
# An instance of a module: the module name, the instance name and an opening parenthesis
reModuleInstance = re.compile(r"^\s+[A-Za-z_\\][^\s(]*\s+([A-Za-z_\\][^\s(]*)\s*\($")
# An instance with parameters: the module name and #(, the parameters, then the instance name on a line of its own
reParameterizedModule = re.compile(r"^\s+[A-Za-z_\\][^\s(]*\s+#\($")
reInstanceName = re.compile(r"^\s+([A-Za-z_\\][^\s(.]*)\s*\($")


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
    bParameters = False
    with open(sVerilogFile, encoding="utf-8", errors="replace") as oFile:
        for sLine in oFile:
            if bParameters:
                oMatch = reInstanceName.match(sLine)
                if oMatch:
                    bParameters = False
                    if oLocation is not None and sModule is not None:
                        dReturn.setdefault((sModule, "instance " + oMatch.group(1)), oLocation)
                continue
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
            oMatch = reModuleInstance.match(sLine)
            if oMatch:
                dReturn.setdefault((sModule, "instance " + oMatch.group(1)), oLocation)
            elif reParameterizedModule.match(sLine):
                bParameters = True
            if sLine.strip() == "" or sLine.startswith("endmodule"):
                oLocation = None
    return dReturn


class Netlist:
    """The modules of a Yosys JSON netlist, with the location of each cell and the names of its nets."""

    def __init__(self, dNetlist, dLocations):
        dModules = dNetlist.get("modules", {})
        # GHDL writes an empty module, marked blackbox, for each component without an entity, such as a vendor
        # primitive: those are black boxes, not modules with no logic
        self.black_boxes = {s: d for s, d in dModules.items() if is_black_box(d)}
        self.modules = {s: d for s, d in dModules.items() if s not in self.black_boxes}
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
        sName = sCell.lstrip("\\")
        oReturn = self.locations.get((module_name(sModule), sName.split(".")[-1]))
        if oReturn is None:
            # GHDL writes the instance data_ram_gen:1.data_ram_inst as data_ram_gen_n1_data_ram_inst
            oReturn = self.locations.get((module_name(sModule), "instance " + verilog_instance_name(sName)))
        return oReturn

    def bit_name(self, sModule, iBit):
        """
        Returns the name of the signal or port a bit belongs to, preferring names written in the VHDL, and among
        them a signal of the architecture over a port it drives, such as busy_r over busy for busy <= busy_r.
        """
        lNames = self.bit_names(sModule, iBit)
        return lNames[0] if lNames else None

    def bit_names(self, sModule, iBit):
        """Returns the names of the signals and ports a bit belongs to, best first, see bit_name."""
        dModule = self.modules.get(sModule, {})
        dPorts = dModule.get("ports", {})
        lReturn = []
        for sName, dNet in dModule.get("netnames", {}).items():
            if iBit in dNet.get("bits", []) and not dNet.get("hide_name"):
                lReturn.append(sName)
        for sName, dPort in dPorts.items():
            if iBit in dPort.get("bits", []) and sName not in lReturn:
                lReturn.append(sName)
        lReturn.sort(key=lambda s: (s.startswith("$"), s in dPorts, s))
        return lReturn


def is_black_box(dModule):
    """Returns whether a module of the netlist is a black box: it has the blackbox attribute."""
    oValue = dModule.get("attributes", {}).get("blackbox")
    if oValue is None:
        return False
    try:
        return int(str(oValue), 2) != 0 if isinstance(oValue, str) else bool(oValue)
    except ValueError:
        return True


def verilog_instance_name(sName):
    """Returns the name GHDL gives an instance in Verilog: generate indexes become _nN and dots underscores."""
    return re.sub(r":(-?\d+)", lambda o: "_n" + o.group(1).replace("-", "m"), sName).replace(".", "_")


def module_name(sModule):
    """Returns a module name as GHDL writes it in Verilog: without the backslash Yosys adds."""
    return sModule.lstrip("\\")
