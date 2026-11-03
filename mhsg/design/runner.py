# -*- coding: utf-8 -*-
"""
Runs GHDL and Yosys on a design:

1. GHDL analyzes the files of each library, in order.
2. GHDL synthesizes the top entity to Verilog. The Verilog is not used as a netlist, only for the location
   comments GHDL writes before each statement, which netlist.py joins to the cells of the Yosys netlist.
3. Yosys synthesizes the same top entity through the GHDL plugin, runs proc and check, and writes a JSON netlist.
   The netlist is taken before any optimization, which would remove and rewrite logic.

Both synthesis runs use the same options, so GHDL numbers the instances the same way in both.
"""

import json
import os
import re
import subprocess

from mhsg.design import top

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
    oResult = Result()
    os.makedirs(sWorkDirectory, exist_ok=True)
    oPatch = top.patch_real_generics(oDesign, sWorkDirectory)
    lPatched = []
    if oPatch is not None:
        sOriginal, sCopy, lPatched = oPatch
        oResult.file_map[sCopy] = sOriginal
    for oLibrary in oDesign.libraries:
        if not oLibrary.files:
            continue
        lFiles = [{v: k for k, v in oResult.file_map.items()}.get(s, s) for s in oLibrary.files]
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
    lCommand = [oTools.yosys, "-m", "ghdl", "-q", "-l", sLog, "-p", sScript]
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
