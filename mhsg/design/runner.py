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
from mhsg.design import tools, top

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
    lOptions += [f"-g{sName}={value_text(oValue)}" for sName, oValue in oDesign.generics.items() if sName.lower() not in setPatched]
    return lOptions


def top_units(oDesign):
    return [oDesign.top] + ([oDesign.architecture] if oDesign.architecture else [])


def value_text(oValue):
    if isinstance(oValue, bool):
        return "true" if oValue else "false"
    return str(oValue)


def run(oDesign, oTools, sWorkDirectory):
    """Runs the steps in the work directory and returns a Result. Stops at the first step that fails."""
    if oDesign.language == "systemverilog":
        return run_verilog(oDesign, oTools, sWorkDirectory)
    oResult = Result()
    os.makedirs(sWorkDirectory, exist_ok=True)
    oPatch = top.patch_real_generics(oDesign, sWorkDirectory)
    lPatched = []
    if oPatch is not None:
        sOriginal, sCopy, lPatched = oPatch
        oResult.file_map[sCopy] = sOriginal
    for oLibrary in oDesign.libraries:
        # The Verilog files of a design of both languages are read by Yosys
        lLibraryFiles = [s for s in oLibrary.files if language.of_file(s) == language.VHDL]
        if not lLibraryFiles:
            continue
        lFiles = [{v: k for k, v in oResult.file_map.items()}.get(s, s) for s in lLibraryFiles]
        lCommand = [oTools.ghdl, "-a"] + ghdl_options(oDesign, sWorkDirectory) + [f"--work={oLibrary.name}"] + lFiles
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
        sRead, lOptions = verilog_read(oDesign, oTools, None)
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
    sRead, lOptions = verilog_read(oDesign, oTools, oDesign.top)
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


def verilog_read(oDesign, oTools, sTop):
    """
    Returns (Yosys commands, Yosys options) that read the Verilog and SystemVerilog files of a design: read_slang when
    Yosys has it, else read_verilog -sv. With sTop, the commands also elaborate that top module with the parameters
    set under generics.
    """
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
