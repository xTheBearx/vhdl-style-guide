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
    stubs.write(oDesign, sWorkDirectory, tools.data_directory(oTools.yosys))
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
    stubs.write(oDesign, sWorkDirectory, tools.data_directory(oTools.yosys))
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
    dCopies = {}
    bSlang = tools.slang_options(oTools.yosys) is not None if getattr(oTools, "slang", False) else False
    if not bSlang:
        tVariants = entity_variants(oDesign, oTools, sWorkDirectory, oResult, dUsed)
        if tVariants is None:
            return oResult
        lCommands += [f"read_json {quote(s)}" for s in tVariants[0]]
        # The instances with generics of their own name the modules elaborated with them, in copies of their files
        dCopies = edited_copies(tVariants[1], sWorkDirectory)
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
    sRead, lOptions = verilog_read_files(oDesign, oTools, oDesign.top, dCopies)
    lFirst = [s for s in lCommands if s.startswith(("read_json", "ghdl", "rename"))]
    lAfter = [s for s in lCommands if s not in lFirst]
    sScript = "; ".join(
        [*lFirst, *([sBlackBoxes] if sBlackBoxes else []), *lAfter, *([sRead] if sRead else []), "proc", "check", f"write_json {quote(sNetlist)}"],
    )
    lCommand = [oTools.yosys, *yosys_module_options(oTools), *lOptions, "-q", "-l", sLog, "-p", sScript]
    oResult.commands.append(lCommand)
    oProcess = subprocess.run(lCommand, capture_output=True, text=True, env=oTools.environment, check=False)
    dOriginals = {v: k for k, v in dCopies.items()}
    oResult.messages.extend(parse_messages(oProcess.stderr, "yosys"))
    for oMessage in parse_verilog_messages(oProcess.stderr, "verilog"):
        oMessage.file = dOriginals.get(oMessage.file, oMessage.file)
        oResult.messages.append(oMessage)
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
        oResult.netlist = original_sources(json.load(oFile), dOriginals)
    return oResult


def entity_variants(oDesign, oTools, sWorkDirectory, oResult, dUsed):
    """
    Elaborates the VHDL entities that Verilog instances give generics of their own, once for each set of values, each
    in a Yosys run of its own, as the ghdl command elaborates one design per run, and writes the modules to JSON files
    named after the variant, such as wrap__mhsg1. The values are those pyslang computes when it elaborates the Verilog
    from its top, so they may be expressions of parameters; an instance in a module with parameters gets the values
    of every elaboration of the module, which must agree. Returns (JSON files, edits), where an edit (file, start,
    end, text) replaces the module name and parameters of an instance, such as wrap #(.N(4)), by the name of its
    variant, or by the name of the entity alone for an instance analyzed with the defaults; or None if a run failed.
    An instance whose generics cannot be set is elaborated with the defaults, with a message that says why.
    """
    lInstances = verilog_black_boxes.parameterized_instances(oDesign, set(dUsed))
    if not lInstances:
        return [], []
    dTypes = {s: top.generic_types(oDesign, s.lower(), dUsed[s]) for s in {o.type for o in lInstances}}
    # The generics of each entity as the Verilog names them, for the module that stands in for it in pyslang
    dSpellings = {s: {k: k for k in d} for s, d in dTypes.items()}
    for oInstance in lInstances:
        for sParameter, _ in oInstance.parameters:
            if sParameter is not None and sParameter.lower() in dSpellings[oInstance.type]:
                dSpellings[oInstance.type][sParameter.lower()] = sParameter
    dElaborated = verilog_black_boxes.elaborated_parameters(oDesign, {s: list(d.values()) for s, d in dSpellings.items()}) if oDesign.top else {}
    dVariants = {}
    lEdits = []
    for oInstance in lInstances:
        lNames = list(dTypes[oInstance.type])
        lSet = []
        for iParameter, (sParameter, sValue) in enumerate(oInstance.parameters):
            # A parameter given by position is the generic declared at that position
            sGeneric = sParameter.lower() if sParameter else (lNames[iParameter] if iParameter < len(lNames) else None)
            if sGeneric is None or sGeneric not in dTypes[oInstance.type]:
                oInstance.problem = oInstance.problem or f"{oInstance.type} has no generic {sParameter or f'at position {iParameter + 1}'}"
                continue
            lSet.append((sGeneric, sValue))
        setValues = set()
        for dValues in dElaborated.get((oInstance.file, oInstance.offset), []) if not oInstance.problem else []:
            setValues.add(tuple(generic_value(dValues.get(dSpellings[oInstance.type][s]), sValue, dTypes[oInstance.type][s], s) for s, sValue in lSet))
        if not oInstance.problem and not setValues:
            # Not met by the elaboration, as in a module the top does not use: only literals can be passed on
            setValues.add(tuple(generic_value(None, sValue, dTypes[oInstance.type][s], s) for s, sValue in lSet))
        if len(setValues) > 1:
            oInstance.problem = f"the elaborations of module {oInstance.module} give it different values"
        elif setValues and any(t[1] is None for t in next(iter(setValues))):
            oInstance.problem = "the value of a parameter could not be computed"
        if oInstance.problem:
            sText = f"Instance {oInstance.name} of {oInstance.type} is analyzed with the defaults of its generics, as its own values cannot be set: {oInstance.problem}"
            oResult.messages.append(Message(oInstance.file, oInstance.line, 0, "error", sText, "configuration"))
            lEdits.append((oInstance.file, *oInstance.span, oInstance.type))
            continue
        lGenerics = [(s, value_text(o, dTypes[oInstance.type][s])) for s, o in next(iter(setValues))]
        dVariants.setdefault((oInstance.type, tuple(sorted(lGenerics))), []).append(oInstance)
    lJson = []
    for iVariant, ((sType, tGenerics), lVariantInstances) in enumerate(sorted(dVariants.items()), start=1):
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
        lJson.append(sJson)
        lEdits += [(o.file, *o.span, sType.lower() + sSuffix) for o in lVariantInstances]
    return lJson, lEdits


def generic_value(oElaborated, sWritten, sType, sGeneric):
    """
    (generic, value) for a parameter of an instance: the value pyslang computed, else the literal as written, or None.
    A string comes from pyslang as the integer of its characters; a boolean as 0 or 1.
    """
    oValue = oElaborated if oElaborated is not None else verilog_black_boxes.literal(sWritten)
    if sType == "string" and isinstance(oValue, int):
        oValue = verilog_black_boxes.literal(sWritten)
        if not isinstance(oValue, str):
            oValue = None
    if sType == "boolean" and oValue in (0, 1):
        oValue = bool(oValue)
    return sGeneric, oValue


def edited_copies(lEdits, sWorkDirectory):
    """
    Writes a copy of each Verilog file with edits, see entity_variants, keeping every line in place, and returns
    {original file: copy}.
    """
    dEdits = {}
    for sFile, iStart, iEnd, sText in lEdits:
        dEdits.setdefault(sFile, set()).add((iStart, iEnd, sText))
    sDirectory = os.path.join(sWorkDirectory, "verilog")
    os.makedirs(sDirectory, exist_ok=True)
    dReturn = {}
    for iFile, (sFile, setEdits) in enumerate(sorted(dEdits.items())):
        with open(sFile, encoding="utf-8", errors="replace", newline="") as oFile:
            sSource = oFile.read()
        for iStart, iEnd, sText in sorted(setEdits, reverse=True):
            sSource = sSource[:iStart] + sText + "\n" * sSource[iStart:iEnd].count("\n") + sSource[iEnd:]
        sCopy = os.path.join(sDirectory, f"{iFile}_{os.path.basename(sFile)}")
        with open(sCopy, "w", encoding="utf-8", newline="") as oFile:
            oFile.write(sSource)
        dReturn[sFile] = sCopy
    return dReturn


def original_sources(oObject, dOriginals):
    """Replaces the names of edited copies by those of the original files in the strings of a netlist."""
    if isinstance(oObject, dict):
        return {k: original_sources(v, dOriginals) for k, v in oObject.items()}
    if isinstance(oObject, list):
        return [original_sources(o, dOriginals) for o in oObject]
    if isinstance(oObject, str):
        for sCopy, sFile in dOriginals.items():
            if sCopy in oObject:
                oObject = oObject.replace(sCopy, sFile)
    return oObject


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


def verilog_read_files(oDesign, oTools, sTop, dCopies=None):
    """Returns (Yosys command, Yosys options) that read the Verilog files of a design, or the copies of dCopies."""
    lDefines = [f"-D{sName}" if oValue is None else f"-D{sName}={verilog_value(oValue)}" for sName, oValue in oDesign.defines.items()]
    lIncludes = [f"-I{quote(s)}" for s in oDesign.include_directories]
    lFiles = [quote((dCopies or {}).get(s, s)) for s in oDesign.verilog_files()]
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
