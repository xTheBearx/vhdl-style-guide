# -*- coding: utf-8 -*-
"""
Reads the JSON netlist of Yosys and maps its cells back to VHDL source locations.

The GHDL plugin for Yosys writes no source locations into the netlist. The cells it creates are named after GHDL's
instance numbers, such as \\17 or :17, and GHDL's Verilog output names the same instance n17_q, n17_o or n17 and gives
it the location of the VHDL statement it came from, as a single line and column. Depending on the version of GHDL the
location is:

- a comment before the statement, such as /* fifo.vhd:42:5 */ or /*# fifo.vhd:42:5 */,
- a Yosys src attribute on the statement or on the declaration of its output, such as
  (* src="fifo.vhd:42.5" *) or (* src="fifo.vhd:42.5-44.9" *), possibly several joined by |,
- or both. Some builds write neither, and their cells have no location.

Joining the instance numbers of the two gives each cell its location. A src attribute on a cell of the JSON netlist,
which holds the same text, is used for the cells the Verilog does not locate.
"""

import os
import re

LATCH_TYPES = {"$dlatch", "$adlatch", "$dlatchsr"}
MUX_TYPES = {"$mux", "$pmux"}
FLIP_FLOP_TYPES = {"$dff", "$dffe", "$adff", "$adffe", "$sdff", "$sdffe", "$sdffce", "$aldff", "$aldffe", "$dffsr", "$dffsre"}

VHDL_EXTENSIONS = (".vhd", ".vhdl", ".vho", ".vhf")

# A location comment of GHDL: /* file:line:column */, or /*# file:line:column */ in later versions
reLocation = re.compile(r"^\s*/\*#?\s*(\S+):(\d+):(\d+)\s*\*/")
# A Verilog attribute instance, (* name = value, ... *), and the src attribute in it
reAttributes = re.compile(r"\(\*.*?\*\)")
reSourceAttribute = re.compile(r'\bsrc\s*=\s*"((?:[^"\\]|\\.)*)"')
# One location of a src attribute: file:line.column or file:line.column-line.column; the column is optional
reSource = re.compile(r"^(.+?):(\d+)(?:\.(\d+))?(?:-\d+(?:\.\d+)?)?$")
reModule = re.compile(r"^\s*module\s+([^\s(;#]+)")
# The output of an instance: n17_q or n17_o, or n17 in later versions, assigned
reInstanceOutput = re.compile(r"\bn(\d+)(?:_[a-z]+)?\b\s*(?:<=|=)")
# The declaration of the output of an instance, such as reg [7:0] n17; or wire n17_o;
reInstanceDeclaration = re.compile(r"^\s*(?:reg|wire|logic)\b(?:\s+signed)?(?:\s*\[[^\]]*\])?\s+n(\d+)(?:_[a-z]+)?\s*[;\[=]")
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


def read_locations(sVerilogFile, lSourceFiles=None):
    """
    Returns {(module, instance number): Location} from the locations in GHDL's Verilog output: the location comments,
    and the src attributes of the statements and of the declarations of instance outputs. An instance gets the src
    attribute of its statement, else the last comment, which holds until a blank line as in the output of earlier
    versions, else the src attribute of the declaration of its output. lSourceFiles, the files of the design, picks
    the location among several in a src attribute, see source_location.
    """
    dReturn = {}
    dDeclarations = {}
    sModule = None
    # The location of the last comment, and of the src attribute of the statement, which holds until the statement ends
    oLocation = None
    oStatement = None
    bParameters = False
    setFiles = source_file_set(lSourceFiles)
    with open(sVerilogFile, encoding="utf-8", errors="replace") as oFile:
        for sLine in oFile:
            oSource = attribute_location(sLine, setFiles)
            sCode = reAttributes.sub("", sLine) if "(*" in sLine else sLine
            if bParameters:
                oCurrent = oSource or oStatement or oLocation
                oMatch = reInstanceName.match(sCode)
                if oMatch:
                    bParameters = False
                    if oCurrent is not None and sModule is not None:
                        dReturn.setdefault((sModule, "instance " + oMatch.group(1)), oCurrent)
                    oStatement = None
                continue
            oMatch = reModule.match(sCode)
            if oMatch:
                sModule, oLocation, oStatement = oMatch.group(1), None, None
                continue
            oMatch = reLocation.match(sCode)
            if oMatch:
                oLocation = Location(oMatch.group(1), int(oMatch.group(2)), int(oMatch.group(3)))
                continue
            if sModule is None:
                continue
            oMatch = reInstanceDeclaration.match(sCode)
            if oMatch:
                # The src attribute of a declaration locates the declared output only, not the statements after it
                if oSource is not None:
                    dDeclarations.setdefault((sModule, oMatch.group(1)), oSource)
            elif oSource is not None:
                oStatement = oSource
            oCurrent = oStatement or oLocation
            if oCurrent is not None:
                for oInstance in reInstanceOutput.finditer(sCode):
                    dReturn.setdefault((sModule, oInstance.group(1)), oCurrent)
                oMatch = reModuleInstance.match(sCode)
                if oMatch:
                    dReturn.setdefault((sModule, "instance " + oMatch.group(1)), oCurrent)
                elif reParameterizedModule.match(sCode):
                    bParameters = True
            if sLine.strip() == "" or sCode.startswith("endmodule"):
                oLocation = None
                oStatement = None
            elif sCode.rstrip().endswith(";"):
                oStatement = None
    for tKey, oDeclaration in dDeclarations.items():
        dReturn.setdefault(tKey, oDeclaration)
    return dReturn


def attribute_location(sLine, setFiles=None):
    """Returns the Location of the src attribute in the attribute instances of a line of Verilog, or None."""
    if "(*" not in sLine:
        return None
    for sAttributes in reAttributes.findall(sLine):
        oMatch = reSourceAttribute.search(sAttributes)
        if oMatch:
            return source_location(oMatch.group(1).replace('\\"', '"'), setFiles)
    return None


def source_location(sSource, setFiles=None):
    """
    Returns the Location of the value of a src attribute, such as fifo.vhd:42.5-44.9, or None if it has no location in
    a VHDL file. Of several locations joined by |, the first in a file of the design, in setFiles, wins, then the first in
    a VHDL file.
    """
    if not isinstance(sSource, str):
        return None
    oFirst = None
    for sPart in sSource.split("|"):
        oMatch = reSource.match(sPart.strip())
        if oMatch is None:
            continue
        sFile = oMatch.group(1)
        oLocation = Location(sFile, int(oMatch.group(2)), int(oMatch.group(3) or 0))
        if setFiles and normalise(sFile) in setFiles:
            # Named as the design names it: read_slang writes the paths it was given relative to its own directory
            if isinstance(setFiles, dict):
                oLocation.file = setFiles[normalise(sFile)]
            return oLocation
        if oFirst is None and sFile.lower().endswith(VHDL_EXTENSIONS):
            oFirst = oLocation
    return oFirst


def source_file_set(lSourceFiles):
    """{normalised path: the path as given} of the files of a design."""
    return {normalise(s): s for s in lSourceFiles} if lSourceFiles else {}


def normalise(sFile):
    return os.path.normcase(os.path.normpath(os.path.abspath(sFile)))


# The attribute of a black box module made for a Verilog design whose inout ports are inputs or outputs by instance,
# see verilog_black_boxes.py
INFERRED_DIRECTIONS = "mhsg_inferred_directions"


def infer_directions(dModules, setTypes):
    """
    Makes each inout port of an instance of the given black box types an input when something else drives the bits it
    connects to, or it connects to constants, and an output otherwise.
    """
    if not setTypes:
        return
    for dModule in dModules.values():
        dCells = dModule.get("cells", {})
        lInstances = [d for d in dCells.values() if d.get("type") in setTypes]
        if not lInstances:
            continue
        setDriven = set()
        for dPort in dModule.get("ports", {}).values():
            if dPort.get("direction") in ("input", "inout"):
                setDriven.update(b for b in dPort.get("bits", []) if isinstance(b, int))
        for dCell in dCells.values():
            dDirections = dCell.get("port_directions", {})
            for sPort, lBits in dCell.get("connections", {}).items():
                if dDirections.get(sPort) == "output" or (dDirections.get(sPort) == "inout" and dCell.get("type") not in setTypes):
                    setDriven.update(b for b in lBits if isinstance(b, int))
        for dCell in lInstances:
            dDirections = dCell.setdefault("port_directions", {})
            for sPort, lBits in dCell.get("connections", {}).items():
                if dDirections.get(sPort) != "inout":
                    continue
                lVariables = [b for b in lBits if isinstance(b, int)]
                dDirections[sPort] = "input" if not lVariables or any(b in setDriven for b in lVariables) else "output"


class Netlist:
    """The modules of a Yosys JSON netlist, with the location of each cell and the names of its nets."""

    def __init__(self, dNetlist, dLocations, lSourceFiles=None):
        dModules = dNetlist.get("modules", {})
        self._setFiles = source_file_set(lSourceFiles)
        # GHDL writes an empty module, marked blackbox, for each component without an entity, such as a vendor
        # primitive: those are black boxes, not modules with no logic
        for dModule in dModules.values():
            normalise_module(dModule)
        self.black_boxes = {s: d for s, d in dModules.items() if is_black_box(d)}
        self.modules = {s: d for s, d in dModules.items() if s not in self.black_boxes}
        self.locations = dLocations
        infer_directions(self.modules, {s for s, d in self.black_boxes.items() if INFERRED_DIRECTIONS in d.get("attributes", {})})

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
        """
        Returns the Location of a cell, or None if it is not known: from the Verilog of GHDL, else from the src
        attribute of the cell in the netlist.
        """
        sName = sCell.lstrip("\\")
        oReturn = self.locations.get((module_name(sModule), instance_number(sName.split(".")[-1])))
        if oReturn is None:
            # GHDL writes the instance data_ram_gen:1.data_ram_inst as data_ram_gen_n1_data_ram_inst
            oReturn = self.locations.get((module_name(sModule), "instance " + verilog_instance_name(sName)))
        if oReturn is None:
            dCell = self.modules.get(sModule, {}).get("cells", {}).get(sCell, {})
            oReturn = source_location(dCell.get("attributes", {}).get("src"), self._setFiles)
            if oReturn is None and dCell:
                oReturn = self.output_location(sModule, sCell, dCell)
        return oReturn

    def output_location(self, sModule, sCell, dCell):
        """
        Returns the Location of the declaration of the signal a cell without a location drives, or None: read_slang
        writes no location on registers, which it names $driver$ and the signal.
        """
        dNetnames = self.modules.get(sModule, {}).get("netnames", {})
        sName = sCell.lstrip("\\")
        if sName.startswith("$driver$"):
            dNet = dNetnames.get(sName[len("$driver$") :]) or dNetnames.get("\\" + sName[len("$driver$") :])
            if dNet is not None:
                return source_location(dNet.get("attributes", {}).get("src"), self._setFiles)
        setBits = {b for sPort in ("Q", "Y") for b in dCell.get("connections", {}).get(sPort, []) if isinstance(b, int)}
        if not setBits:
            return None
        for sNet, dNet in dNetnames.items():
            if dNet.get("hide_name") or sNet.startswith("$") or not setBits & set(dNet.get("bits", [])):
                continue
            oLocation = source_location(dNet.get("attributes", {}).get("src"), self._setFiles)
            if oLocation is not None:
                return oLocation
        return None

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


def normalise_module(dModule):
    """
    Makes the netlist of read_slang look like that of read_verilog and GHDL, in place: the nets a $buf cell joins,
    which read_slang writes for continuous assignments, become one net, and a register loaded asynchronously with a
    constant, $aldff, which read_slang writes for an asynchronous reset, becomes a register with an asynchronous reset.
    """
    dCells = dModule.get("cells", {})
    dAlias = {}
    for sCell, dCell in list(dCells.items()):
        if dCell.get("type") != "$buf":
            continue
        dConnections = dCell.get("connections", {})
        lA, lY = dConnections.get("A", []), dConnections.get("Y", [])
        if len(lA) != len(lY) or any(isinstance(b, int) and b in dAlias for b in lY):
            continue
        for oA, oY in zip(lA, lY):
            if isinstance(oY, int):
                dAlias[oY] = oA
        del dCells[sCell]
    if dAlias:

        def resolve(oBit):
            setSeen = set()
            while isinstance(oBit, int) and oBit in dAlias and oBit not in setSeen:
                setSeen.add(oBit)
                oBit = dAlias[oBit]
            return oBit

        for dPort in dModule.get("ports", {}).values():
            dPort["bits"] = [resolve(b) for b in dPort.get("bits", [])]
        for dNet in dModule.get("netnames", {}).values():
            dNet["bits"] = [resolve(b) for b in dNet.get("bits", [])]
        for dCell in dCells.values():
            dCell["connections"] = {k: [resolve(b) for b in v] for k, v in dCell.get("connections", {}).items()}
    for dCell in dCells.values():
        if dCell.get("type") not in ("$aldff", "$aldffe"):
            continue
        dConnections = dCell.get("connections", {})
        lData = dConnections.get("AD", [])
        if not lData or "ALOAD" not in dConnections or not all(b in ("0", "1") for b in lData):
            continue
        dParameters = dCell.setdefault("parameters", {})
        dCell["type"] = "$adff" if dCell["type"] == "$aldff" else "$adffe"
        dConnections["ARST"] = dConnections.pop("ALOAD")
        del dConnections["AD"]
        dParameters["ARST_POLARITY"] = dParameters.pop("ALOAD_POLARITY", "1")
        dParameters["ARST_VALUE"] = "".join(reversed(lData))
        if "port_directions" in dCell:
            dDirections = dCell["port_directions"]
            dDirections.pop("AD", None)
            dDirections["ARST"] = dDirections.pop("ALOAD", "input")


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


def instance_number(sName):
    """Returns the instance number of a cell the GHDL plugin names \\17 or :17, as 17; other names unchanged."""
    return sName[1:] if sName.startswith(":") and sName[1:].isdigit() else sName


def module_name(sModule):
    """
    Returns a module name as GHDL writes it in Verilog: without the backslash Yosys adds, and without what follows a
    $ in the name of a copy of the module for one instance, such as ibex_alu$ibex_core.alu_i of read_slang.
    """
    sName = sModule.lstrip("\\")
    if not sName.startswith("$") and "$" in sName:
        sName = sName.split("$")[0]
    return sName
