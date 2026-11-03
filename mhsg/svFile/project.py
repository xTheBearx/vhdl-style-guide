# -*- coding: utf-8 -*-
"""
Lint of the SystemVerilog files of a run as one design.

In lint mode, the SystemVerilog files of a run, those given with --index_files and those listed under files in the
systemverilog section of the configuration are compiled together once, before the files are checked. Each file then
gets the warnings slang found in it, with the modules, packages and macros of the other files known: unused,
undriven and implicit signals are checked wherever everything a file uses is in the run, and the connections of
instances are checked against the modules they instantiate.
"""

import hashlib
import os

import pyslang
from pyslang import analysis, ast  # pylint: disable=import-error
from pyslang.syntax import SyntaxTree  # pylint: disable=import-error

from mhsg import config, language
from mhsg.svFile import lint, preprocessor
from mhsg.vhdlFile import utils


def text_hash(sText):
    return hashlib.sha1(sText.encode("utf-8", errors="surrogateescape")).hexdigest()


def file_text(sFileName):
    """The text of a file as svFile parses it: its lines without their line ends, each ended with a new line."""
    lLines, eError = utils.read_vhdlfile(sFileName)
    if eError:
        return None
    return "\n".join(lLines) + "\n" if lLines else ""


def files_of_run(lFiles, dConfig):
    """The SystemVerilog files among the files of a run, then those listed under files in the systemverilog section."""
    lReturn = []
    dSection = (dConfig or {}).get("systemverilog") or {}
    lExtra = []
    for sPattern in dSection.get("files") or [] if isinstance(dSection, dict) else []:
        sPattern = os.path.expandvars(str(sPattern))
        lExtra.extend(config.glob_filenames(sPattern) or [sPattern])
    for sFile in list(lFiles) + lExtra:
        sPath = os.path.abspath(sFile)
        if language.of_file(sFile) == language.SYSTEMVERILOG and os.path.isfile(sPath) and sPath not in lReturn:
            lReturn.append(sPath)
    return lReturn


def collect(lFiles, dConfig):
    """
    Compiles the SystemVerilog files of a run together and returns {absolute file name: entry}, where an entry holds
    the hash of the text compiled, the warnings as (offset, name, message), and whether the file uses something
    unknown to the run.
    """
    lPaths = files_of_run(lFiles, dConfig)
    if not lPaths:
        return {}
    oOptions = preprocessor.options(dConfig)
    oSourceManager = pyslang.SourceManager()
    oCompilation = ast.Compilation()
    dBuffers = {}
    lTrees = []
    # Every file gets its buffer before any is parsed, so a file another one includes is read once, as it is here
    lBuffers = []
    for sPath in lPaths:
        sText = file_text(sPath)
        if sText is None:
            continue
        oBuffer = oSourceManager.assignText(sPath, sText)
        lBuffers.append(oBuffer)
        dBuffers[oBuffer.id.id] = (sPath, text_hash(sText))
    for oBuffer in lBuffers:
        oTree = SyntaxTree.fromBuffer(oBuffer, oSourceManager, oOptions) if oOptions is not None else SyntaxTree.fromBuffer(oBuffer, oSourceManager)
        oCompilation.addSyntaxTree(oTree)
        lTrees.append(oTree)
    lDiagnostics = list(oCompilation.getAllDiagnostics())
    oCompilation.freeze()
    oAnalysisOptions = analysis.AnalysisOptions()
    oAnalysisOptions.flags = analysis.AnalysisFlags.CheckUnused
    oAnalysis = analysis.AnalysisManager(oAnalysisOptions)
    oAnalysis.analyze(oCompilation)
    lDiagnostics.extend(oAnalysis.getDiagnostics())
    oEngine = pyslang.DiagnosticEngine(oCompilation.sourceManager)
    dReturn = {sPath: {"hash": sHash, "diagnostics": [], "incomplete": False} for sPath, sHash in dBuffers.values()}
    for oTree in lTrees:
        lDiagnostics.extend(oTree.diagnostics)
    for oDiagnostic in lDiagnostics:
        tFile = dBuffers.get(oDiagnostic.location.buffer.id)
        if tFile is None:
            continue
        dEntry = dReturn[tFile[0]]
        sName = lint.diagnostic_name(oDiagnostic)
        if oDiagnostic.isError():
            if sName in lint.UNKNOWN:
                dEntry["incomplete"] = True
            continue
        tDiagnostic = (oDiagnostic.location.offset, sName, oEngine.formatMessage(oDiagnostic))
        if tDiagnostic not in dEntry["diagnostics"]:
            dEntry["diagnostics"].append(tDiagnostic)
    return dReturn
