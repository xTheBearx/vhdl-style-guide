# -*- coding: utf-8 -*-
"""
The lint model of a SystemVerilog file: slang elaborates the file and analyzes its procedures, which finds width
mismatches, inferred latches, multiple drivers, unused declarations and more.

A file is linted on its own, so modules, packages and macros of other files are unknown. slang reports those as
errors and leaves out the warnings that would follow from them; the model keeps only warnings. When the file uses
anything unknown, a signal driven or read there looks undriven or unused, so the model leaves those warnings out, as
it does the unused members of a package, which other files use. In lint mode the files of a run are compiled
together instead, see project.py, and a file only falls back to this model when a fix changed it.
"""

import pyslang
from pyslang import analysis, ast  # pylint: disable=import-error

# Warnings that need everything the file uses to be known
UNDRIVEN = ("UnassignedVariable", "UndrivenPort", "UndrivenNet")
# Errors of a file linted on its own that use something defined elsewhere
UNKNOWN = ("UnknownModule", "UnknownInterface", "UnknownPackage", "UnknownClass", "UnknownDirective", "UndeclaredIdentifier", "UnknownSystemName")


def is_undriven_or_unused(sName):
    """Warnings that something used from another file can cause: undriven, unused and implicitly declared."""
    return sName in UNDRIVEN or sName.startswith(("Unused", "ImplicitNet"))


class Diagnostic:
    """A warning of slang: where it is in the file, its name, such as WidthTruncate, and its message."""

    def __init__(self, iOffset, sName, sMessage):
        self.offset = iOffset
        self.name = sName
        self.message = sMessage


class LintModel:
    def __init__(self, oTree, iBuffer=None):
        self.diagnostics = []
        # True when the file uses modules, packages, macros or names defined elsewhere
        self.incomplete = False
        if oTree is None:
            return
        oCompilation = ast.Compilation()
        oCompilation.addSyntaxTree(oTree)
        lDiagnostics = list(oCompilation.getAllDiagnostics())
        oCompilation.freeze()
        oOptions = analysis.AnalysisOptions()
        oOptions.flags = analysis.AnalysisFlags.CheckUnused
        oAnalysis = analysis.AnalysisManager(oOptions)
        oAnalysis.analyze(oCompilation)
        lDiagnostics.extend(oAnalysis.getDiagnostics())
        oEngine = pyslang.DiagnosticEngine(oCompilation.sourceManager)
        if iBuffer is None and oTree.root.getFirstToken() is not None:
            iBuffer = oTree.root.getFirstToken().location.buffer.id
        setSeen = set()
        lAll = list(oTree.diagnostics) + lDiagnostics
        self.incomplete = any(oDiagnostic.isError() and diagnostic_name(oDiagnostic) in UNKNOWN for oDiagnostic in lAll)
        oSourceManager = oCompilation.sourceManager
        for oDiagnostic in lDiagnostics:
            oLocation = original_location(oSourceManager, oDiagnostic.location)
            if oDiagnostic.isError() or oLocation.buffer.id != iBuffer:
                continue
            sName = diagnostic_name(oDiagnostic)
            if self.incomplete and is_undriven_or_unused(sName):
                continue
            sMessage = oEngine.formatMessage(oDiagnostic)
            if sName.startswith("Unused") and sMessage.startswith("unused package"):
                # A package is used by other files: linted on its own, all of it looks unused
                continue
            tKey = (oLocation.offset, sName)
            if tKey in setSeen:
                continue
            setSeen.add(tKey)
            self.diagnostics.append(Diagnostic(oLocation.offset, sName, sMessage))
        self.diagnostics.sort(key=lambda o: o.offset)

    @classmethod
    def from_project(cls, dEntry):
        """The model of a file from the compilation of the whole run, see project.py."""
        oModel = cls(None)
        oModel.incomplete = dEntry["incomplete"]
        for iOffset, sName, sMessage in sorted(dEntry["diagnostics"]):
            if oModel.incomplete and is_undriven_or_unused(sName):
                continue
            oModel.diagnostics.append(Diagnostic(iOffset, sName, sMessage))
        return oModel

    def named(self, fMatch):
        """The diagnostics whose name fMatch accepts."""
        return [o for o in self.diagnostics if fMatch(o.name)]


def diagnostic_name(oDiagnostic):
    """The name of a slang diagnostic, such as WidthTruncate."""
    return str(oDiagnostic.code).replace("DiagCode(", "").rstrip(")")


def original_location(oSourceManager, oLocation):
    """The location of a diagnostic in the file: in the arguments of a macro use for one in the code they expand to."""
    try:
        if oSourceManager.isMacroArgLoc(oLocation):
            return oSourceManager.getFullyOriginalLoc(oLocation)
    except (RuntimeError, ValueError, TypeError):
        pass
    return oLocation
