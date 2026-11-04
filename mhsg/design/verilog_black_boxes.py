# -*- coding: utf-8 -*-
"""
Black boxes in Verilog and SystemVerilog designs: the modules the design instantiates but no file defines, such as
vendor primitives, encrypted IP or cores delivered as netlists.

Yosys stops at an instance of a module it does not know, so each gets a module with ports and no logic, read as a
black box (read_verilog -lib) before the design. GHDL writes the same kind of module for a VHDL component without an
entity, so the rules treat both alike, and design_017 asks for a declaration of each.

The ports and their directions come, in this order, from:
  the cell models Yosys has for a vendor, when the design names its black box library (black_box_libraries: [xilinx]);
  the declaration of the black box: a clock, an enable, a reset input or a static port is an input, a path, a clock
  output, a reset output or a synchronized output is an output, and so is each port another role names as its input;
  otherwise the port is an input of an instance if something else drives what it connects to, and an output if not.
The ports are those the instances connect by name, and those the declaration names without a pattern.
"""

import os
import re

import pyslang  # pylint: disable=import-error
from pyslang import ast  # pylint: disable=import-error
from pyslang.syntax import SyntaxKind, SyntaxTree  # pylint: disable=import-error

from mhsg.svFile import preprocessor, verilator

# Yosys' cell models of the vendors whose black box libraries come with mhsg, under its data directory (+/)
YOSYS_MODELS = {
    "xilinx": ["xilinx/cells_sim.v", "xilinx/cells_xtra.v"],
    "lattice": ["ecp5/cells_sim.v", "ecp5/cells_bb.v", "ice40/cells_sim.v"],
    "microchip": ["sf2/cells_sim.v"],
}

# The attribute of a stub whose inout ports are made inputs or outputs for each instance, see netlist.py
INFERRED_DIRECTIONS = "mhsg_inferred_directions"

INPUT_ROLES = ("clock", "enable", "reset_in", "static")
OUTPUT_ROLES = ("path", "clock_out", "reset_out", "synchronized")


def trees(oDesign):
    """The pyslang syntax trees of the Verilog and SystemVerilog files of a design, with its defines."""
    return [oTree for _, oTree in file_trees(oDesign)]


def file_trees(oDesign):
    """(file name, pyslang syntax tree) of each Verilog and SystemVerilog file of a design, with its defines."""
    oOptions = preprocessor.options({"systemverilog": {"defines": oDesign.defines, "include_directories": oDesign.include_directories}})
    lReturn = []
    for sFile in oDesign.verilog_files():
        try:
            lReturn.append((sFile, SyntaxTree.fromFile(sFile, oOptions) if oOptions is not None else SyntaxTree.fromFile(sFile)))
        except (OSError, RuntimeError, ValueError):
            continue
    return lReturn


def undefined_modules(oDesign, setExclude=()):
    """
    Returns {module: what its instances name} for the modules the Verilog files instantiate but do not define, leaving
    out those in setExclude, such as VHDL entities.
    """
    if not oDesign.verilog_files():
        return {}
    dReturn = verilator.undefined_modules(trees(oDesign))
    return {k: v for k, v in dReturn.items() if k not in setExclude}


class Instance:
    """An instance of a VHDL entity in the Verilog of a design, with the parameters it sets."""

    def __init__(self, sModule, sName, sType, sFile, iLine):
        self.module = sModule
        self.name = sName
        self.type = sType
        self.file = sFile
        self.line = iLine
        # The offset of its name in the file, and the span of its module name and parameters, such as wrap #(.N(4))
        self.offset = None
        self.span = None
        # (parameter name, or None for a parameter given by position, value as written)
        self.parameters = []
        # Why the instance cannot have its own generics, or ""
        self.problem = ""


def parameterized_instances(oDesign, setTypes):
    """The instances of the modules of setTypes, such as VHDL entities, that set parameters."""
    lReturn = []
    for sFile, oTree in file_trees(oDesign):
        for oModule in verilator.nodes(oTree):
            if oModule.kind not in verilator.DEFINITIONS:
                continue
            sModule = verilator.name_of(oModule.header.name)
            for oNode in verilator.descendants(oModule):
                if oNode.kind != SyntaxKind.HierarchyInstantiation or verilator.name_of(oNode.type) not in setTypes or oNode.parameters is None:
                    continue
                oLast = oNode.parameters.getLastToken()
                tSpan = (oNode.type.location.offset, oLast.location.offset + len(oLast.rawText))
                for oInstance in verilator.elements(oNode.instances):
                    if oInstance.decl is None:
                        continue
                    oLocation = oInstance.decl.name.location
                    sName = verilator.name_of(oInstance.decl.name)
                    oItem = Instance(sModule, sName, verilator.name_of(oNode.type), sFile, oTree.sourceManager.getLineNumber(oLocation))
                    oItem.offset = oLocation.offset
                    oItem.span = tSpan
                    for oParameter in verilator.elements(oNode.parameters.parameters):
                        sValue = str(oParameter.expr).strip() if oParameter.expr is not None else ""
                        if oParameter.kind == SyntaxKind.NamedParamAssignment:
                            oItem.parameters.append((verilator.name_of(oParameter.name), sValue))
                        else:
                            oItem.parameters.append((None, sValue))
                    lReturn.append(oItem)
    return lReturn


def elaborated_parameters(oDesign, dStandIns):
    """
    Elaborates the Verilog of a design from its top with pyslang, each VHDL entity of dStandIns ({module as the Verilog
    names it: [its generics, in order, as the Verilog names them]}) standing in as a module with those parameters, and
    returns {(file, offset of the name of an instance of an entity): [{parameter: value}, ...]}, a dictionary for each
    time the elaboration meets the instance, as a module with parameters can be elaborated several times. A value is
    an integer, a real as text, or None if it has x or z bits; a string comes as the integer of its characters.
    """
    oOptions = preprocessor.options({"systemverilog": {"defines": oDesign.defines, "include_directories": oDesign.include_directories}})
    oCompilationOptions = ast.CompilationOptions()
    oCompilationOptions.topModules = {oDesign.top}
    oCompilationOptions.paramOverrides = [f"{k}={verilog_text(v)}" for k, v in oDesign.generics.items()]
    oSourceManager = pyslang.SourceManager()
    oCompilation = ast.Compilation(pyslang.Bag([oCompilationOptions]))
    dFiles = {}
    for sFile in oDesign.verilog_files():
        try:
            with open(sFile, encoding="utf-8", errors="replace") as oFile:
                oBuffer = oSourceManager.assignText(sFile, oFile.read())
        except OSError:
            continue
        dFiles[oBuffer.id.id] = sFile
        oCompilation.addSyntaxTree(
            SyntaxTree.fromBuffer(oBuffer, oSourceManager, oOptions) if oOptions is not None else SyntaxTree.fromBuffer(oBuffer, oSourceManager),
        )
    lStubs = []
    for sModule, lParameters in dStandIns.items():
        lStubs.append(f"module {sModule} #(" + ", ".join(f"parameter {s} = 0" for s in lParameters) + ") (); endmodule")
    oCompilation.addSyntaxTree(SyntaxTree.fromText("\n".join(lStubs), oSourceManager, "mhsg_entities.sv"))
    dReturn = {}

    def visit(oSymbol):
        if oSymbol.kind.name != "Instance" or oSymbol.definition.name not in dStandIns:
            return
        sFile = dFiles.get(oSymbol.location.buffer.id)
        if sFile is None:
            return
        dValues = {o.name: constant(o.value) for o in oSymbol.body.parameters}
        dReturn.setdefault((sFile, oSymbol.location.offset), []).append(dValues)

    oCompilation.getRoot().visit(visit)
    return dReturn


def constant(oValue):
    """The Python value of a pyslang constant: an integer, a real as text, or None for one with x or z bits."""
    oPython = getattr(oValue, "value", None)
    if isinstance(oPython, float):
        return repr(oPython)
    sText = str(oValue).strip()
    bNegative = sText.startswith("-")
    oInteger = literal(sText.lstrip("-"))
    if not isinstance(oInteger, int):
        return None
    return -oInteger if bNegative else oInteger


def verilog_text(oValue):
    """A value as Verilog writes it: 1 and 0 for booleans, a quoted string for text that is not a number."""
    if isinstance(oValue, bool):
        return "1" if oValue else "0"
    if isinstance(oValue, str) and literal(oValue) is None:
        return '"' + oValue + '"'
    return str(oValue)


def literal(sValue):
    """The value of a Verilog literal parameter: an integer, a real or a string as text; None for an expression."""
    sValue = sValue.strip().replace("_", "")
    if re.fullmatch(r"\d+", sValue):
        return int(sValue)
    oMatch = re.fullmatch(r"\d*'[sS]?([dDhHbBoO])([0-9a-fA-F]+)", sValue)
    if oMatch:
        return int(oMatch.group(2), {"d": 10, "h": 16, "b": 2, "o": 8}[oMatch.group(1).lower()])
    if re.fullmatch(r"\d+\.\d+(?:[eE][+-]?\d+)?", sValue):
        return sValue
    if len(sValue) >= 2 and sValue[0] == '"' and sValue[-1] == '"':
        return sValue[1:-1]
    return None


def defined_modules(oDesign):
    """The names of the modules, interfaces and programs the Verilog and SystemVerilog files define."""
    return {verilator.name_of(o.header.name) for oTree in trees(oDesign) for o in verilator.nodes(oTree) if o.kind in verilator.DEFINITIONS}


reDirection = re.compile(r"\b(input|output|inout)\b\s*(?:wire\b|reg\b|signed\b|\[[^\]]*\]|\s)*([A-Za-z_][\w$]*(?:\s*,\s*[A-Za-z_][\w$]*)*)")


def model_directions(sDataDirectory, lFiles, setModules):
    """
    Returns {module: {port: input | output | inout}} for the modules of setModules that Yosys' cell model files define,
    with the directions the models declare, in the header or the body.
    """
    dReturn = {}
    setWanted = {s.lower() for s in setModules}
    for sFile in lFiles:
        try:
            with open(os.path.join(sDataDirectory, sFile), encoding="utf-8", errors="replace") as oFile:
                sText = re.sub(r"//[^\n]*|/\*.*?\*/", "", oFile.read(), flags=re.DOTALL)
        except OSError:
            continue
        for oMatch in re.finditer(r"^\s*module\s+([A-Za-z_][\w$]*)(.*?)^\s*endmodule", sText, re.MULTILINE | re.DOTALL):
            sModule = oMatch.group(1)
            if sModule.lower() not in setWanted or sModule.lower() in {s.lower() for s in dReturn}:
                continue
            dPorts = {}
            for oPort in reDirection.finditer(oMatch.group(2)):
                for sPort in oPort.group(2).split(","):
                    dPorts.setdefault(sPort.strip(), oPort.group(1))
            dReturn[sModule] = dPorts
    return dReturn


def model_modules(sDataDirectory, lFiles):
    """Returns {module: model file} for the modules of Yosys' cell model files."""
    dReturn = {}
    for sFile in lFiles:
        sPath = os.path.join(sDataDirectory, sFile)
        try:
            with open(sPath, encoding="utf-8", errors="replace") as oFile:
                sText = oFile.read()
        except OSError:
            continue
        for sModule in re.findall(r"^\s*module\s+([A-Za-z_][A-Za-z0-9_$]*)", sText, re.MULTILINE):
            dReturn.setdefault(sModule, sFile)
    return dReturn


def directions(oDesign, sModule, lPorts):
    """Returns {port: input | output | inout} for the ports of a black box, from its declarations."""
    lDeclarations = oDesign.black_boxes.find(sModule, "")
    dReturn = {}
    setInputs = set()
    for oDeclaration in lDeclarations:
        for _, oRole in oDeclaration.ports:
            if oRole is None:
                continue
            setInputs.update(s.lower() for s in list(oRole.inputs) + [oRole.source, oRole.clock] if s)
    for sPort in lPorts:
        sDirection = "input" if sPort.lower() in setInputs else "inout"
        for oDeclaration in lDeclarations:
            bFound, oRole = oDeclaration.role(sPort, {})
            if bFound and oRole is not None:
                if oRole.kind in INPUT_ROLES:
                    sDirection = "input"
                elif oRole.kind in OUTPUT_ROLES:
                    sDirection = "output"
                break
        dReturn[sPort] = sDirection
    return dReturn


def declared_ports(oDesign, sModule):
    """The ports the declarations of a black box name without a pattern."""
    lReturn = []
    for oDeclaration in oDesign.black_boxes.find(sModule, ""):
        for sPattern, oRole in oDeclaration.ports:
            if not any(c in sPattern for c in "*?[") and sPattern not in lReturn:
                lReturn.append(sPattern)
            for sName in oRole.names() if oRole is not None else []:
                if sName not in lReturn:
                    lReturn.append(sName)
    return lReturn


def stub(oDesign, sModule, dInstances):
    """The text of a module with the ports and parameters of a black box and no logic."""
    lPorts = list(dInstances["ports"])
    for sPort in declared_ports(oDesign, sModule):
        if not any(s.lower() == sPort.lower() for s in lPorts):
            lPorts.append(sPort)
    lPorts += [f"mhsg_port_{i}" for i in range(dInstances["ordered_ports"]) if f"mhsg_port_{i}" not in lPorts]
    lParameters = dInstances["parameters"] + [f"mhsg_parameter_{i}" for i in range(dInstances["ordered_parameters"])]
    dDirections = directions(oDesign, sModule, lPorts)
    sParameters = " #(" + ", ".join(f"parameter {s} = 0" for s in lParameters) + ")" if lParameters else ""
    sPorts = " (" + ", ".join(f"{dDirections[s]} wire {s}" for s in lPorts) + ")" if lPorts else ""
    # The inout ports of each instance are made inputs or outputs from what drives them, see netlist.py
    sAttribute = f"(* {INFERRED_DIRECTIONS} *) " if "inout" in dDirections.values() else ""
    return f"{sAttribute}module {sModule}{sParameters}{sPorts};\nendmodule\n"


def read_commands(oDesign, sWorkDirectory, sDataDirectory, lLibraries, setExclude=()):
    """
    Returns the Yosys commands that read the black boxes of a design, or "" if it has none: Yosys' cell models of the
    vendors in lLibraries that define some of them, and a file of stubs for the others, written to the work directory.
    Modules in setExclude, such as the VHDL entities of a Verilog top, are not black boxes.
    """
    dUndefined = undefined_modules(oDesign, setExclude)
    if not dUndefined:
        return ""
    dModels = model_modules(sDataDirectory, [s for sLibrary in lLibraries for s in YOSYS_MODELS.get(sLibrary, [])])
    lModelFiles = []
    lStubs = []
    for sModule, dInstances in dUndefined.items():
        sModel = dModels.get(sModule)
        if sModel is not None:
            if sModel not in lModelFiles:
                lModelFiles.append(sModel)
        else:
            lStubs.append(stub(oDesign, sModule, dInstances))
    lCommands = [f"read_verilog -lib -specify +/{s}" for s in lModelFiles]
    if lStubs:
        sStubFile = os.path.join(sWorkDirectory, "black_boxes.v")
        with open(sStubFile, "w", encoding="utf-8") as oFile:
            oFile.write("// Black boxes: modules the design instantiates but no file defines, see mhsg/design/verilog_black_boxes.py\n")
            oFile.write("".join(lStubs))
        lCommands.append(f"read_verilog -lib {sStubFile}")
    return "; ".join(lCommands)
