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

from pyslang.syntax import SyntaxTree  # pylint: disable=import-error

from mhsg.svFile import preprocessor, verilator

# Yosys' cell models of the vendors whose black box libraries come with mhsg, under its data directory (+/)
YOSYS_MODELS = {
    "xilinx": ["xilinx/cells_sim.v", "xilinx/cells_xtra.v"],
}

# The attribute of a stub whose inout ports are made inputs or outputs for each instance, see netlist.py
INFERRED_DIRECTIONS = "mhsg_inferred_directions"

INPUT_ROLES = ("clock", "enable", "reset_in", "static")
OUTPUT_ROLES = ("path", "clock_out", "reset_out", "synchronized")


def undefined_modules(oDesign):
    """Returns {module: what its instances name} for the modules the Verilog files instantiate but do not define."""
    lFiles = oDesign.verilog_files()
    if not lFiles:
        return {}
    oOptions = preprocessor.options({"systemverilog": {"defines": oDesign.defines, "include_directories": oDesign.include_directories}})
    lTrees = []
    for sFile in lFiles:
        try:
            lTrees.append(SyntaxTree.fromFile(sFile, oOptions) if oOptions is not None else SyntaxTree.fromFile(sFile))
        except (OSError, RuntimeError, ValueError):
            continue
    return verilator.undefined_modules(lTrees)


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


def read_commands(oDesign, sWorkDirectory, sDataDirectory, lLibraries):
    """
    Returns the Yosys commands that read the black boxes of a design, or "" if it has none: Yosys' cell models of the
    vendors in lLibraries that define some of them, and a file of stubs for the others, written to the work directory.
    """
    dUndefined = undefined_modules(oDesign)
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
