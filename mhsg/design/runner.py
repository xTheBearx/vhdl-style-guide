# -*- coding: utf-8 -*-
"""
Runs GHDL and Yosys on a design:

1. GHDL analyzes the files of each library, in order.
2. GHDL synthesizes the top entity to Verilog. The Verilog is not used as a netlist, only for the locations GHDL
   writes for each statement, as comments or src attributes, which netlist.py joins to the cells of the Yosys netlist.
3. Yosys synthesizes the same top entity through the GHDL plugin, loaded with -m ghdl unless it is built into Yosys,
   runs proc and check, and writes a JSON netlist.
   The netlist is taken before any optimization, which would remove and rewrite logic.

Both synthesis runs use the same options, so GHDL numbers the instances the same way in both.
"""

import json
import os
import re
import subprocess

from mhsg import language
from mhsg.design import stubs, tools, top, verilog_black_boxes

# GHDL writes file:line:column:severity: text, or file:line:column:(assert severity): text for assertion reports
reMessage = re.compile(
    r"^(?P<file>.+?):(?P<line>\d+):(?P<column>\d+):\s*(?:(?P<severity>error|warning|note):|\(assert (?P<assert>note|warning|error|failure)\):|\(report (?P<report>note|warning|error|failure)\):)?\s*(?P<text>.*)$",
)


class Message:
    """A message from GHDL with its location."""

    def __init__(self, sFile, iLine, iColumn, sSeverity, sText, sStage):
        self.file = sFile
        self.line = iLine
        self.column = iColumn
        self.severity = sSeverity
        self.text = sText
        self.stage = sStage


class Result:
    def __init__(self):
        # The step that failed: analysis, elaboration or yosys; None if every step ran
        self.failed_stage = None
        self.messages = []
        self.verilog_file = None
        self.netlist = None
        self.yosys_log = ""
        self.commands = []
        # Patched copy of a file -> the original, whose name the findings use
        self.file_map = {}

    def unpatch(self, sText):
        """Replaces the names of patched copies in the output of a tool with the names of the original files."""
        for sCopy, sOriginal in self.file_map.items():
            sText = sText.replace(sCopy, sOriginal)
        return sText


def ghdl_options(oDesign, sWorkDirectory):
    return [f"--std={oDesign.standard}", f"--workdir={sWorkDirectory}", f"-P{sWorkDirectory}"] + oDesign.ghdl_options


def elaboration_options(oDesign, sWorkDirectory, lPatched=()):
    """
    Returns the options for elaborating the top entity; they come before the unit names, see top_units.
    Generics in lPatched are set in a copy of the top file instead, see top.patch_real_generics.
    """
    lOptions = ghdl_options(oDesign, sWorkDirectory) + [f"--work={oDesign.top_library}", "--latches"]
    setPatched = {s.lower() for s in lPatched}
    dTypes = top.generic_types(oDesign) if oDesign.generics else {}
    lOptions += [f"-g{sName}={value_text(oValue, dTypes.get(sName.lower()))}" for sName, oValue in oDesign.generics.items() if sName.lower() not in setPatched]
    return lOptions


def top_units(oDesign):
    return [oDesign.top] + ([oDesign.architecture] if oDesign.architecture else [])


def value_text(oValue, sType=None):
    """A generic's value as GHDL takes it on the command line; a single character of a character type, such as 1 for a
    std_logic, is quoted as a character literal."""
    if isinstance(oValue, bool):
        return "true" if oValue else "false"
    sValue = str(oValue)
    if sType in top.CHARACTER_TYPES and len(sValue) == 1:
        return f"'{sValue}'"
    return sValue


def analysis_groups(oDesign, oTools, sWorkDirectory, oResult, lTops=None):
    """
    Returns the VHDL files to analyze as (library, files) pairs, in the order they are analyzed, or None if GHDL could
    not find the order; its messages are then in oResult. The Verilog files of a design of both languages are read
    by Yosys. With order: listed, each library's files in the order of the configuration. With order: auto, the files
    the top entity needs, in the order GHDL gives (--elab-order) after importing every file into a directory of its
    own; consecutive files of one library are analyzed together. Files the top does not need are left out.
    """
    lListed = [(o.name, [s for s in o.files if language.of_file(s) == language.VHDL]) for o in oDesign.libraries]
    lListed = [(sLibrary, lFiles) for sLibrary, lFiles in lListed if lFiles]
    if oDesign.order != "auto":
        return lListed
    sDirectory = os.path.join(sWorkDirectory, "order")
    os.makedirs(sDirectory, exist_ok=True)
    lOptions = [f"--std={oDesign.standard}", f"--workdir={sDirectory}", f"-P{sDirectory}"] + oDesign.ghdl_options
    iMessages = len(oResult.messages)
    dLibraries = {}
    for sLibrary, lFiles in lListed:
        # GHDL 4.1 leaves files imported by an absolute path out of --elab-order, so the paths are relative
        lRelative = [relative_path(s) for s in lFiles]
        if not run_ghdl(oResult, oTools, [oTools.ghdl, "-i"] + lOptions + [f"--work={sLibrary}"] + lRelative, "analysis"):
            return None
        for sFile in lFiles:
            dLibraries.setdefault(os.path.abspath(sFile), (sLibrary, sFile))
    # The top entity, or for a Verilog top the VHDL entities it instantiates, as (library, units)
    lTops = lTops if lTops is not None else [(oDesign.top_library, top_units(oDesign))]
    lOrder = []
    for iTop, (sLibrary, lUnits) in enumerate(lTops):
        sOrder = os.path.join(sDirectory, f"order{iTop}.txt")
        lCommand = [oTools.ghdl, "--elab-order"] + lOptions + [f"--work={sLibrary}"] + lUnits
        if not run_ghdl(oResult, oTools, lCommand, "analysis", sOrder):
            return None
        with open(sOrder, encoding="utf-8") as oFile:
            lOrder += [s.strip() for s in oFile.read().splitlines() if s.strip()]
    # The warnings of these steps, such as unbound components, come again when the design is analyzed and elaborated
    del oResult.messages[iMessages:]
    lGroups = []
    setDone = set()
    for sLine in lOrder:
        tFile = dLibraries.get(os.path.abspath(sLine))
        if tFile is None or tFile in setDone:
            continue
        setDone.add(tFile)
        if lGroups and lGroups[-1][0] == tFile[0]:
            lGroups[-1][1].append(tFile[1])
        else:
            lGroups.append((tFile[0], [tFile[1]]))
    if not lGroups:
        oResult.failed_stage = "analysis"
        oResult.messages.append(Message(None, 0, 0, "error", f"GHDL gave no compile order for {oDesign.top} (order: auto)", "analysis"))
        return None
    return lGroups


def relative_path(sFile):
    """Returns the path of a file relative to the current directory, or as it is if there is none, as on another drive."""
    try:
        return os.path.relpath(sFile)
    except ValueError:
        return sFile


def run(oDesign, oTools, sWorkDirectory):
    """Runs the steps in the work directory and returns a Result. Stops at the first step that fails."""
    if oDesign.language == "systemverilog":
        return run_verilog(oDesign, oTools, sWorkDirectory)
    if oDesign.language == "mixed" and oDesign.top in verilog_black_boxes.defined_modules(oDesign):
        return run_verilog_top(oDesign, oTools, sWorkDirectory)
    oResult = Result()
    os.makedirs(sWorkDirectory, exist_ok=True)
    stubs.write(oDesign, sWorkDirectory)
    oPatch = top.patch_real_generics(oDesign, sWorkDirectory)
    lPatched = []
    if oPatch is not None:
        sOriginal, sCopy, lPatched = oPatch
        oResult.file_map[sCopy] = sOriginal
    lGroups = analysis_groups(oDesign, oTools, sWorkDirectory, oResult)
    if lGroups is None:
        return oResult
    for sLibrary, lLibraryFiles in lGroups:
        lFiles = [{v: k for k, v in oResult.file_map.items()}.get(s, s) for s in lLibraryFiles]
        lCommand = [oTools.ghdl, "-a"] + ghdl_options(oDesign, sWorkDirectory) + [f"--work={sLibrary}"] + lFiles
        if not run_ghdl(oResult, oTools, lCommand, "analysis"):
            return oResult

    oResult.verilog_file = os.path.join(sWorkDirectory, "design.v")
    lCommand = [oTools.ghdl, "synth"] + elaboration_options(oDesign, sWorkDirectory, lPatched) + ["--out=verilog"] + top_units(oDesign)
    if not run_ghdl(oResult, oTools, lCommand, "elaboration", oResult.verilog_file):
        return oResult

    sNetlist = os.path.join(sWorkDirectory, "design.json")
    sLog = os.path.join(sWorkDirectory, "yosys.log")
    sScript = "ghdl " + " ".join(elaboration_options(oDesign, sWorkDirectory, lPatched) + top_units(oDesign)) + f"; proc; check; write_json {sNetlist}"
    lOptions = []
    if oDesign.verilog_files():
        # The Verilog modules the VHDL instantiates are read first; hierarchy links the instances GHDL leaves unbound
        sRead, lOptions = verilog_read(oDesign, oTools, None, sWorkDirectory)
        sScript = sRead + "; ghdl " + " ".join(elaboration_options(oDesign, sWorkDirectory, lPatched) + top_units(oDesign))
        sScript += f"; hierarchy -check -top {oDesign.top}; proc; check; write_json {sNetlist}"
    lCommand = [oTools.yosys, *yosys_module_options(oTools), *lOptions, "-q", "-l", sLog, "-p", sScript]
    oResult.commands.append(lCommand)
    oProcess = subprocess.run(lCommand, capture_output=True, text=True, env=oTools.environment, check=False)
    oResult.messages.extend(parse_messages(oResult.unpatch(oProcess.stderr), "yosys"))
    if os.path.isfile(sLog):
        with open(sLog, encoding="utf-8", errors="replace") as oFile:
            oResult.yosys_log = oFile.read()
    if oProcess.returncode != 0 or not os.path.isfile(sNetlist):
        oResult.failed_stage = "yosys"
        return oResult
    with open(sNetlist, encoding="utf-8") as oFile:
        oResult.netlist = json.load(oFile)
    return oResult


def run_verilog(oDesign, oTools, sWorkDirectory):
    """Runs Yosys on a design of Verilog and SystemVerilog files and returns a Result."""
    oResult = Result()
    os.makedirs(sWorkDirectory, exist_ok=True)
    sNetlist = os.path.join(sWorkDirectory, "design.json")
    sLog = os.path.join(sWorkDirectory, "yosys.log")
    sRead, lOptions = verilog_read(oDesign, oTools, oDesign.top, sWorkDirectory)
    sScript = f"{sRead}; proc; check; write_json {quote(sNetlist)}"
    lCommand = [oTools.yosys, *lOptions, "-q", "-l", sLog, "-p", sScript]
    oResult.commands.append(lCommand)
    oProcess = subprocess.run(lCommand, capture_output=True, text=True, env=oTools.environment, check=False)
    oResult.messages.extend(parse_verilog_messages(oProcess.stderr, "verilog"))
    if os.path.isfile(sLog):
        with open(sLog, encoding="utf-8", errors="replace") as oFile:
            oResult.yosys_log = oFile.read()
    if oProcess.returncode != 0 or not os.path.isfile(sNetlist):
        oResult.failed_stage = "verilog"
        if not any(o.severity in (None, "error") for o in oResult.messages):
            sText = (oProcess.stderr.strip() or "Yosys failed").splitlines()[-1]
            oResult.messages.append(Message(None, 0, 0, "error", sText, "verilog"))
        return oResult
    with open(sNetlist, encoding="utf-8") as oFile:
        oResult.netlist = json.load(oFile)
    return oResult


reEntity = re.compile(r"^\s*entity\s+([a-z]\w*)\s+is\b", re.IGNORECASE | re.MULTILINE)


def vhdl_entities(oDesign):
    """{entity name in lower case: library} of the VHDL files of a design."""
    dReturn = {}
    for oLibrary in oDesign.libraries:
        for sFile in oLibrary.files:
            if language.of_file(sFile) != language.VHDL:
                continue
            try:
                with open(sFile, encoding="utf-8", errors="replace") as oFile:
                    sText = re.sub(r"--[^\n]*", "", oFile.read())
            except OSError:
                continue
            for sEntity in reEntity.findall(sText):
                dReturn.setdefault(sEntity.lower(), oLibrary.name)
    return dReturn


def run_verilog_top(oDesign, oTools, sWorkDirectory):
    """
    Runs a design of both languages whose top is a Verilog module: GHDL analyzes the VHDL, Yosys elaborates each VHDL
    entity the Verilog instantiates with the ghdl command, with the defaults of its generics, then reads the Verilog
    and elaborates the top module.
    """
    oResult = Result()
    os.makedirs(sWorkDirectory, exist_ok=True)
    stubs.write(oDesign, sWorkDirectory)
    dVhdlEntities = vhdl_entities(oDesign)
    # The VHDL entities the Verilog instantiates, as the Verilog names them
    dUsed = {s: dVhdlEntities[s.lower()] for s in verilog_black_boxes.undefined_modules(oDesign) if s.lower() in dVhdlEntities}
    lTops = [(sLibrary, [sModule.lower()]) for sModule, sLibrary in dUsed.items()]
    lGroups = analysis_groups(oDesign, oTools, sWorkDirectory, oResult, lTops) if lTops or oDesign.order != "auto" else []
    if lGroups is None:
        return oResult
    for sLibrary, lFiles in lGroups:
        lCommand = [oTools.ghdl, "-a"] + ghdl_options(oDesign, sWorkDirectory) + [f"--work={sLibrary}"] + lFiles
        if not run_ghdl(oResult, oTools, lCommand, "analysis"):
            return oResult
    lCommands = []
    lRetarget = []
    bSlang = tools.slang_options(oTools.yosys) is not None if getattr(oTools, "slang", False) else False
    if not bSlang:
        lVariants = entity_variants(oDesign, oTools, sWorkDirectory, oResult, dUsed)
        if lVariants is None:
            return oResult
        for sJson, lInstances in lVariants:
            if sJson is not None:
                lCommands.append(f"read_json {quote(sJson)}")
            lRetarget += lInstances
    for sModule, sLibrary in dUsed.items():
        lCommands.append("ghdl " + " ".join(ghdl_options(oDesign, sWorkDirectory) + [f"--work={sLibrary}", "--latches", sModule.lower()]))
        if sModule != sModule.lower():
            # GHDL names the module in lower case; Verilog names it as written
            lCommands.append(f"rename {sModule.lower()} {sModule}")
    sNetlist = os.path.join(sWorkDirectory, "design.json")
    sLog = os.path.join(sWorkDirectory, "yosys.log")
    sBlackBoxes = verilog_black_boxes.read_commands(
        oDesign,
        sWorkDirectory,
        tools.data_directory(oTools.yosys),
        oDesign.black_box_libraries,
        set(dUsed),
    )
    if lRetarget:
        # Each instance with generics of its own is retargeted to the module elaborated with them, before the hierarchy
        sRead, lOptions = verilog_read_files(oDesign, oTools, None)
        lCommands += [sRead]
        for sModule, sCell, sVariant, lParameters in lRetarget:
            if sVariant is not None:
                lCommands.append(f"chtype -set {sVariant} {sModule}/{sCell}")
            # A parameter given by position is named $1, $2 and so on until the hierarchy is elaborated
            lCommands += [f"setparam -unset {sParameter} {sModule}/{sCell}" for sParameter in lParameters]
        lCommands.append(" ".join(["hierarchy -check -top", oDesign.top, *[f"-chparam {k} {verilog_value(v)}" for k, v in oDesign.generics.items()]]))
        sRead = ""
    else:
        sRead, lOptions = verilog_read_files(oDesign, oTools, oDesign.top)
    lFirst = [s for s in lCommands if s.startswith(("read_json", "ghdl", "rename"))]
    lAfter = [s for s in lCommands if s not in lFirst]
    sScript = "; ".join(
        [*lFirst, *([sBlackBoxes] if sBlackBoxes else []), *lAfter, *([sRead] if sRead else []), "proc", "check", f"write_json {quote(sNetlist)}"],
    )
    lCommand = [oTools.yosys, *yosys_module_options(oTools), *lOptions, "-q", "-l", sLog, "-p", sScript]
    oResult.commands.append(lCommand)
    oProcess = subprocess.run(lCommand, capture_output=True, text=True, env=oTools.environment, check=False)
    oResult.messages.extend(parse_messages(oProcess.stderr, "yosys"))
    oResult.messages.extend(parse_verilog_messages(oProcess.stderr, "verilog"))
    if os.path.isfile(sLog):
        with open(sLog, encoding="utf-8", errors="replace") as oFile:
            oResult.yosys_log = oFile.read()
    if oProcess.returncode != 0 or not os.path.isfile(sNetlist):
        oResult.failed_stage = "verilog"
        if not any(o.severity in (None, "error") for o in oResult.messages):
            sText = (oProcess.stderr.strip() or "Yosys failed").splitlines()[-1]
            oResult.messages.append(Message(None, 0, 0, "error", sText, "verilog"))
        return oResult
    with open(sNetlist, encoding="utf-8") as oFile:
        oResult.netlist = json.load(oFile)
    return oResult


def entity_variants(oDesign, oTools, sWorkDirectory, oResult, dUsed):
    """
    Elaborates the VHDL entities that Verilog instances give generics of their own, once for each set of values, each
    in a Yosys run of its own, as the ghdl command elaborates one design per run, and writes the modules to JSON files
    named after the variant, such as wrap__mhsg1. Returns [(JSON file, [(module, instance, variant, parameters)])], or
    None if a run failed. An instance whose generics cannot be set this way is elaborated with the defaults, with a
    warning that says why.
    """
    dVariants = {}
    dCells = {}
    lDefaults = []
    for oInstance in verilog_black_boxes.parameterized_instances(oDesign, set(dUsed)):
        dTypes = top.generic_types(oDesign, oInstance.type.lower(), dUsed[oInstance.type])
        lNames = list(dTypes)
        lGenerics = []
        for iParameter, (sParameter, sValue) in enumerate(oInstance.parameters):
            # A parameter given by position is the generic declared at that position
            sGeneric = sParameter or (lNames[iParameter] if iParameter < len(lNames) else None)
            oValue = verilog_black_boxes.literal(sValue)
            if sGeneric is None:
                oInstance.problem = oInstance.problem or f"{oInstance.type} has no generic at position {iParameter + 1}"
                continue
            if dTypes.get(sGeneric.lower()) == "boolean" and oValue in (0, 1):
                oValue = bool(oValue)
            lGenerics.append((sGeneric.lower(), value_text(oValue, dTypes.get(sGeneric.lower()))))
        tCell = (oInstance.module, oInstance.cell)
        if not oInstance.problem and dCells.get(tCell, lGenerics) != lGenerics:
            oInstance.problem = f"another instance named {oInstance.name} in a generate block of {oInstance.module} sets other values"
        dCells.setdefault(tCell, lGenerics)
        if oInstance.problem:
            sText = f"Instance {oInstance.name} of {oInstance.type} is analyzed with the defaults of its generics, as its own values cannot be set: {oInstance.problem}"
            oResult.messages.append(Message(oInstance.file, oInstance.line, 0, "error", sText, "configuration"))
            # Its parameters are dropped, so the hierarchy finds the module elaborated with the defaults
            lParameters = [s or f"${i + 1}" for i, (s, _) in enumerate(oInstance.parameters)]
            lDefaults.append((oInstance.module, oInstance.cell, None, lParameters))
            continue
        tKey = (oInstance.type, tuple(sorted(lGenerics)))
        dVariants.setdefault(tKey, []).append((oInstance, [s or f"${i + 1}" for i, (s, _) in enumerate(oInstance.parameters)]))
    lReturn = [(None, lDefaults)] if lDefaults else []
    for iVariant, ((sType, tGenerics), lInstances) in enumerate(sorted(dVariants.items()), start=1):
        sSuffix = f"__mhsg{iVariant}"
        sJson = os.path.join(sWorkDirectory, f"{sType.lower()}{sSuffix}.json")
        lOptions = ghdl_options(oDesign, sWorkDirectory) + [f"--work={dUsed[sType]}", "--latches", *[f"-g{k}={v}" for k, v in tGenerics]]
        sScript = "ghdl " + " ".join(lOptions + [sType.lower()]) + f"; write_json {quote(sJson)}"
        lCommand = [oTools.yosys, *yosys_module_options(oTools), "-q", "-p", sScript]
        oResult.commands.append(lCommand)
        oProcess = subprocess.run(lCommand, capture_output=True, text=True, env=oTools.environment, check=False)
        oResult.messages.extend(parse_messages(oProcess.stderr, "elaboration"))
        if oProcess.returncode != 0 or not os.path.isfile(sJson):
            oResult.failed_stage = "elaboration"
            if not any(o.severity in (None, "error") for o in oResult.messages):
                sText = (oProcess.stderr.strip() or "Yosys failed").splitlines()[-1]
                oResult.messages.append(Message(None, 0, 0, "error", sText, "elaboration"))
            return None
        rename_modules(sJson, sSuffix)
        lReturn.append((sJson, [(o.module, o.cell, sType.lower() + sSuffix, lParameters) for o, lParameters in lInstances]))
    return lReturn


def rename_modules(sJson, sSuffix):
    """Adds a suffix to the names of the modules of a Yosys JSON netlist, and to the cells that instantiate them."""
    with open(sJson, encoding="utf-8") as oFile:
        dNetlist = json.load(oFile)
    setNames = set(dNetlist.get("modules", {}))
    dModules = {}
    for sName, dModule in dNetlist.get("modules", {}).items():
        for dCell in dModule.get("cells", {}).values():
            if dCell.get("type") in setNames:
                dCell["type"] += sSuffix
        dModules[sName + sSuffix] = dModule
    dNetlist["modules"] = dModules
    with open(sJson, "w", encoding="utf-8") as oFile:
        json.dump(dNetlist, oFile)


def verilog_read(oDesign, oTools, sTop, sWorkDirectory=None):
    """
    Returns (Yosys commands, Yosys options) that read the Verilog and SystemVerilog files of a design: read_slang when
    Yosys has it, else read_verilog -sv. With sTop, the commands also elaborate that top module with the parameters
    set under generics. With a work directory, the black boxes are read first, see verilog_black_boxes.py.
    """
    sBlackBoxes = (
        verilog_black_boxes.read_commands(oDesign, sWorkDirectory, tools.data_directory(oTools.yosys), oDesign.black_box_libraries) if sWorkDirectory else ""
    )
    sScript, lOptions = verilog_read_files(oDesign, oTools, sTop)
    return (sBlackBoxes + "; " + sScript if sBlackBoxes else sScript), lOptions


def verilog_read_files(oDesign, oTools, sTop):
    lDefines = [f"-D{sName}" if oValue is None else f"-D{sName}={verilog_value(oValue)}" for sName, oValue in oDesign.defines.items()]
    lIncludes = [f"-I{quote(s)}" for s in oDesign.include_directories]
    lFiles = [quote(s) for s in oDesign.verilog_files()]
    lSlang = tools.slang_options(oTools.yosys) if getattr(oTools, "slang", False) else None
    if lSlang is not None:
        lTop = [f"--top {sTop}"] + [f"-G {sName}={verilog_value(oValue)}" for sName, oValue in oDesign.generics.items()] if sTop else []
        return " ".join(["read_slang", *lDefines, *lIncludes, *lTop, *lFiles]), lSlang
    sScript = " ".join(["read_verilog -sv", *lDefines, *lIncludes, *lFiles])
    if sTop:
        lParameters = [f"-chparam {sName} {verilog_value(oValue)}" for sName, oValue in oDesign.generics.items()]
        sScript += "; " + " ".join(["hierarchy -check -top", sTop, *lParameters])
    return sScript, []


def verilog_value(oValue):
    """A value as Verilog writes it: 1 and 0 for booleans, a quoted string for text."""
    if isinstance(oValue, bool):
        return "1" if oValue else "0"
    if isinstance(oValue, str) and not re.fullmatch(r"[0-9]+('[sS]?[bBoOdDhH][0-9a-fA-F_xXzZ]+)?|'[sS]?[bBoOdDhH][0-9a-fA-F_xXzZ]+", oValue):
        return '"' + oValue + '"'
    return str(oValue)


def quote(sText):
    return '"' + sText + '"' if " " in sText else sText


reVerilogMessage = re.compile(r"^(?P<file>.+?\.(?:sv|svh|v|vh)):(?P<line>\d+): (?P<severity>ERROR|Warning): (?P<text>.*)$", re.IGNORECASE)


def parse_verilog_messages(sOutput, sStage):
    """Returns the messages of Yosys reading and elaborating Verilog: located ones, and errors without a location."""
    lReturn = []
    for sLine in sOutput.splitlines():
        sLine = sLine.strip()
        oMatch = reVerilogMessage.match(sLine)
        if oMatch:
            lReturn.append(Message(oMatch.group("file"), int(oMatch.group("line")), 0, oMatch.group("severity").lower(), oMatch.group("text"), sStage))
        elif sLine.startswith("ERROR: "):
            lReturn.append(Message(None, 0, 0, "error", sLine[len("ERROR: ") :].replace("`\\", "`"), sStage))
    return lReturn


def yosys_module_options(oTools):
    """Returns the options that load the GHDL plugin into Yosys: -m ghdl, or none when it is built into Yosys."""
    fOptions = getattr(oTools, "module_options", None)
    return fOptions() if fOptions is not None else ["-m", "ghdl"]


def run_ghdl(oResult, oTools, lCommand, sStage, sOutput=None):
    """Runs a GHDL command, records its messages, and returns True if it succeeded."""
    oResult.commands.append(lCommand)
    oProcess = subprocess.run(lCommand, capture_output=True, text=True, env=oTools.environment, check=False)
    oResult.messages.extend(parse_messages(oResult.unpatch(oProcess.stderr), sStage))
    if sOutput is not None:
        with open(sOutput, "w", encoding="utf-8") as oFile:
            oFile.write(oResult.unpatch(oProcess.stdout))
    if oProcess.returncode != 0:
        oResult.failed_stage = sStage
        if not any(o.severity in (None, "error") for o in oResult.messages if o.stage == sStage):
            # A failure without a located message, such as an unknown top entity
            sText = (oProcess.stderr.strip() or oProcess.stdout.strip() or "GHDL failed").splitlines()[0]
            oResult.messages.append(Message(None, 0, 0, "error", sText, sStage))
        return False
    return True


def parse_messages(sOutput, sStage):
    """Returns the located messages in the output of GHDL or of the GHDL plugin."""
    lReturn = []
    for sLine in sOutput.splitlines():
        oMatch = reMessage.match(sLine.strip())
        if oMatch is None or not oMatch.group("file").lower().endswith((".vhd", ".vhdl", ".vho", ".vhf")):
            continue
        sSeverity = oMatch.group("severity")
        sAssert = oMatch.group("assert") or oMatch.group("report")
        if sAssert is not None:
            # An assertion of the design reports a problem only with severity error or failure
            sSeverity = "error" if sAssert in ("error", "failure") else sAssert
        sText = oMatch.group("text") if sAssert is None else f"assertion {sAssert}: {oMatch.group('text')}"
        lReturn.append(Message(oMatch.group("file"), int(oMatch.group("line")), int(oMatch.group("column")), sSeverity, sText, sStage))
    return lReturn
