# -*- coding: utf-8 -*-
"""
Verilator's lint of the SystemVerilog files of a run, an optional check besides slang's, see sv_lint_011.

In lint mode, when Verilator is installed, it lints the files of the run together once (verilator --lint-only -Wall),
with the defines and include directories of the systemverilog section. Its warnings become diagnostics of the files,
named verilator.CODE, such as verilator.BLKSEQ. The systemverilog section turns it off with verilator: false, or names
the program with verilator: /path/to/verilator.

Verilator needs a package before the files that import it, so files defining packages come first; and it stops at an
instance of a module it cannot find, so each module the run instantiates but does not define gets a stub, with the
ports and parameters its instances name. When Verilator stops at an error in some files all the same, it runs again
without them, and the error is reported once.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile

from pyslang.syntax import SyntaxKind  # pylint: disable=import-error

from mhsg.rules.sv_tree import descendants, elements, name_of
from mhsg.svFile import preprocessor

reMessage = re.compile(r"^%(?P<kind>Warning|Error)(?:-(?P<code>[A-Z0-9_]+))?: (?P<file>.+?):(?P<line>\d+):(?P<column>\d+): (?P<text>.*)$")

DEFINITIONS = (SyntaxKind.ModuleDeclaration, SyntaxKind.InterfaceDeclaration, SyntaxKind.ProgramDeclaration)


def nodes(oTree):
    """The syntax nodes of a tree; its root is the declaration itself when a file holds only one."""
    yield oTree.root
    yield from descendants(oTree.root)


def find(dConfig):
    """Returns the Verilator program to run, or None when it is not installed or turned off."""
    dSection = (dConfig or {}).get("systemverilog")
    oSetting = dSection.get("verilator", True) if isinstance(dSection, dict) else True
    if oSetting is False or oSetting is None:
        return None
    if isinstance(oSetting, str):
        return shutil.which(os.path.expandvars(oSetting))
    return shutil.which("verilator")


def version(sVerilator):
    """Returns the first line of verilator --version, or None."""
    try:
        oProcess = subprocess.run([sVerilator, "--version"], capture_output=True, text=True, check=False, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return (oProcess.stdout.strip().splitlines() or [None])[0]


def packages(oTree):
    """Returns (the packages a tree defines, the packages and classes it uses by name::)."""
    setDefines = set()
    setUses = set()
    for oNode in nodes(oTree):
        if oNode.kind == SyntaxKind.PackageDeclaration:
            setDefines.add(name_of(oNode.header.name))
        elif oNode.kind == SyntaxKind.PackageImportItem:
            setUses.add(name_of(oNode.package))
        elif oNode.kind == SyntaxKind.ScopedName and oNode.left.kind == SyntaxKind.IdentifierName:
            setUses.add(name_of(oNode.left.identifier))
    return setDefines, setUses - setDefines


def without_unknown_packages(lFiles):
    """
    Returns the files that import no package missing from the files: a file importing one, such as uvm_pkg, stops
    Verilator, and so does a file importing a package of a file left out for that reason.
    """
    dPackages = {sPath: packages(oTree) for sPath, oTree in lFiles}
    setDefinedClasses = set()
    for _, oTree in lFiles:
        for oNode in nodes(oTree):
            if oNode.kind == SyntaxKind.ClassDeclaration:
                setDefinedClasses.add(name_of(oNode.name))
    lActive = list(lFiles)
    while True:
        setDefined = {s for sPath, _ in lActive for s in dPackages[sPath][0]} | setDefinedClasses
        lKept = [(sPath, oTree) for sPath, oTree in lActive if dPackages[sPath][1] <= setDefined]
        if len(lKept) == len(lActive):
            return lKept
        lActive = lKept


def compile_order(lFiles):
    """
    Returns the files, as (path, syntax tree), with each file that defines a package before the files that use it;
    otherwise in the order given. Files that use each other's packages keep their order.
    """
    dDefines = {}
    dUses = {}
    for sPath, oTree in lFiles:
        dDefines[sPath], dUses[sPath] = packages(oTree)
    dDefinedIn = {}
    for sPath, _ in lFiles:
        for sPackage in dDefines[sPath]:
            dDefinedIn.setdefault(sPackage, sPath)
    lReturn = []
    setPlaced = set()
    setVisiting = set()

    def place(sPath, oTree):
        if sPath in setPlaced or sPath in setVisiting:
            return
        setVisiting.add(sPath)
        for sPackage in sorted(dUses[sPath]):
            sDefinition = dDefinedIn.get(sPackage)
            if sDefinition is not None and sDefinition != sPath:
                place(sDefinition, dict(lFiles)[sDefinition])
        setVisiting.discard(sPath)
        setPlaced.add(sPath)
        lReturn.append((sPath, oTree))

    for sPath, oTree in lFiles:
        place(sPath, oTree)
    return lReturn


def stubs(lTrees):
    """Returns the text of empty modules for the modules the trees instantiate but do not define."""
    setDefined = set()
    dInstances = {}
    for oTree in lTrees:
        for oNode in nodes(oTree):
            if oNode.kind in DEFINITIONS:
                setDefined.add(name_of(oNode.header.name))
            elif oNode.kind == SyntaxKind.HierarchyInstantiation:
                dModule = dInstances.setdefault(name_of(oNode.type), {"parameters": [], "ordered_parameters": 0, "ports": [], "ordered_ports": 0})
                if oNode.parameters is not None:
                    lParameters = elements(oNode.parameters.parameters)
                    dModule["ordered_parameters"] = max(
                        dModule["ordered_parameters"],
                        sum(1 for o in lParameters if o.kind == SyntaxKind.OrderedParamAssignment),
                    )
                    for oParameter in lParameters:
                        if oParameter.kind == SyntaxKind.NamedParamAssignment and name_of(oParameter.name) not in dModule["parameters"]:
                            dModule["parameters"].append(name_of(oParameter.name))
                for oInstance in elements(oNode.instances):
                    lConnections = elements(oInstance.connections)
                    dModule["ordered_ports"] = max(dModule["ordered_ports"], sum(1 for o in lConnections if o.kind == SyntaxKind.OrderedPortConnection))
                    for oConnection in lConnections:
                        if oConnection.kind == SyntaxKind.NamedPortConnection and name_of(oConnection.name) not in dModule["ports"]:
                            dModule["ports"].append(name_of(oConnection.name))
    lText = []
    for sModule, dModule in sorted(dInstances.items()):
        if sModule in setDefined or not sModule:
            continue
        lParameters = dModule["parameters"] + [f"mhsg_parameter_{i}" for i in range(dModule["ordered_parameters"])]
        lPorts = dModule["ports"] + [f"mhsg_port_{i}" for i in range(dModule["ordered_ports"])]
        sParameters = " #(" + ", ".join(f"parameter {s} = 0" for s in lParameters) + ")" if lParameters else ""
        sPorts = " (" + ", ".join(f"input wire {s}" for s in lPorts) + ")" if lPorts else ""
        lText.append(f"module {sModule}{sParameters}{sPorts};\nendmodule\n")
    return "".join(lText)


def command(sVerilator, lPaths, dConfig, sStubFile):
    lDefines, lIncludes = preprocessor.settings(dConfig)
    lCommand = [sVerilator, "--lint-only", "-Wall", "-Wno-fatal", "--no-timing", "-Wno-MULTITOP", "-Wno-DECLFILENAME"]
    # As slang does, an included file is also looked for in the directory of the file including it
    lDirectories = list(dict.fromkeys(list(lIncludes) + [os.path.dirname(s) for s in lPaths]))
    lCommand += [f"+incdir+{s}" for s in lDirectories]
    lCommand += [f"-D{s}" for s in lDefines]
    if sStubFile is not None:
        lCommand.append(sStubFile)
    return lCommand + lPaths


# The most times Verilator runs, each without the files it stopped at before
MAX_ROUNDS = 10


def lint(sVerilator, lFiles, dConfig, dTexts):
    """
    Lints the files, given as (path, syntax tree), with Verilator and returns their warnings as
    (path, byte offset, name, message). dTexts holds the text of each file, to turn line and column into an offset.
    Files slang cannot parse are left out, and when Verilator stops at an error in some files all the same, it runs
    again without them; their checks are left out.
    """
    # Files slang cannot parse or preprocess, such as those including a file it cannot find, stop Verilator too
    # and so do files importing a package no file of the run defines
    lActive = without_unknown_packages([(sPath, oTree) for sPath, oTree in lFiles if not any(o.isError() for o in oTree.diagnostics)])
    setActive = {sPath for sPath, _ in lActive}
    lLeftOut = [sPath for sPath, _ in lFiles if sPath not in setActive]
    lErrors = [(lLeftOut[0], "slang cannot parse it, or it imports a package no file of the run defines")] if lLeftOut else []
    lWarnings = []
    for _ in range(MAX_ROUNDS):
        oResult = run(sVerilator, lActive, dConfig)
        if oResult is None:
            return []
        lWarnings, lRoundErrors = oResult
        if not lRoundErrors:
            break
        lErrors.extend(lRoundErrors)
        setStopped = {sPath for sPath, _ in lRoundErrors}
        lStopped = [sPath for sPath, _ in lActive if sPath in setStopped]
        if not lStopped:
            break
        lLeftOut.extend(lStopped)
        lActive = [(sPath, oTree) for sPath, oTree in lActive if sPath not in setStopped]
        if not lActive:
            lWarnings = []
            break
    if lErrors:
        sFiles = f"{len(lLeftOut)} file" + ("s" if len(lLeftOut) != 1 else "") if lLeftOut else "the files"
        print(f"WARNING: Verilator's checks are left out for {sFiles} it stopped at, such as {lErrors[0][0]}: {lErrors[0][1]}", file=sys.stderr)
    lReturn = []
    dLines = {}
    setActive = {sPath for sPath, _ in lActive}
    for sPath, iLine, iColumn, sCode, sText in lWarnings:
        if sPath not in dTexts or sPath not in setActive:
            continue
        if sPath not in dLines:
            dLines[sPath] = line_starts(dTexts[sPath])
        iOffset = offset(dTexts[sPath], dLines[sPath], iLine, iColumn)
        if iOffset is not None:
            lReturn.append((sPath, iOffset, "verilator." + sCode, sText))
    return lReturn


def run(sVerilator, lFiles, dConfig):
    """
    Runs Verilator once on the files, with stubs for the modules they instantiate but do not define. Returns
    (warnings as (path, line, column, code, message), errors as (path, message)), or None if it could not run.
    """
    lOrdered = compile_order(lFiles)
    sStubs = stubs([oTree for _, oTree in lFiles])
    with tempfile.TemporaryDirectory(prefix="mhsg_verilator_") as sDirectory:
        sStubFile = None
        if sStubs:
            sStubFile = os.path.join(sDirectory, "mhsg_stubs.sv")
            with open(sStubFile, "w", encoding="utf-8") as oFile:
                oFile.write("// verilator lint_off UNUSEDSIGNAL\n// verilator lint_off UNUSEDPARAM\n" + sStubs)
        lCommand = command(sVerilator, [sPath for sPath, _ in lOrdered], dConfig, sStubFile)
        try:
            oProcess = subprocess.run(lCommand, capture_output=True, text=True, check=False, cwd=sDirectory)
        except OSError as e:
            print(f"WARNING: Verilator could not run, its checks are left out: {e}", file=sys.stderr)
            return None
    lWarnings = []
    lErrors = []
    for sLine in oProcess.stderr.splitlines():
        oMatch = reMessage.match(sLine)
        if oMatch is None:
            continue
        sPath = os.path.abspath(os.path.join(sDirectory, oMatch.group("file")))
        if oMatch.group("kind") == "Error":
            lErrors.append((sPath, f"{oMatch.group('text')} (line {oMatch.group('line')})"))
        elif oMatch.group("code"):
            lWarnings.append((sPath, int(oMatch.group("line")), int(oMatch.group("column")), oMatch.group("code"), oMatch.group("text")))
    return lWarnings, lErrors


def line_starts(sText):
    """The character offsets at which the lines of a text start."""
    lStarts = [0]
    for oMatch in re.finditer("\n", sText):
        lStarts.append(oMatch.end())
    return lStarts


def offset(sText, lStarts, iLine, iColumn):
    """The byte offset, as slang counts, of a line and column as Verilator gives them, both counted from 1."""
    if iLine < 1 or iLine > len(lStarts):
        return None
    iStart = lStarts[iLine - 1]
    sBefore = sText[:iStart] + sText[iStart : iStart + max(iColumn - 1, 0)]
    return len(sBefore.encode("utf-8", errors="surrogateescape"))
