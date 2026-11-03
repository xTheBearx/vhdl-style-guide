# -*- coding: utf-8 -*-
"""
The lint model of a SystemVerilog file: slang elaborates the file and analyzes its procedures, which finds width
mismatches, inferred latches, multiple drivers, unused declarations and more.

A file is linted on its own, so modules, packages and macros of other files are unknown. slang reports those as
errors and leaves out the warnings that would follow from them; the model keeps only warnings. When the file uses
anything unknown, a signal driven or read there looks undriven or unused, so the model leaves those warnings out.
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
    def __init__(self, oTree):
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
        iBuffer = oTree.root.getFirstToken().location.buffer.id if oTree.root.getFirstToken() is not None else None
        setSeen = set()
        lAll = list(oTree.diagnostics) + lDiagnostics
        self.incomplete = any(oDiagnostic.isError() and diagnostic_name(oDiagnostic) in UNKNOWN for oDiagnostic in lAll)
        for oDiagnostic in lDiagnostics:
            if oDiagnostic.isError() or oDiagnostic.location.buffer.id != iBuffer:
                continue
            sName = diagnostic_name(oDiagnostic)
            if self.incomplete and is_undriven_or_unused(sName):
                continue
            tKey = (oDiagnostic.location.offset, sName)
            if tKey in setSeen:
                continue
            setSeen.add(tKey)
            self.diagnostics.append(Diagnostic(oDiagnostic.location.offset, sName, oEngine.formatMessage(oDiagnostic)))
        self.diagnostics.sort(key=lambda o: o.offset)

    def named(self, fMatch):
        """The diagnostics whose name fMatch accepts."""
        return [o for o in self.diagnostics if fMatch(o.name)]


def diagnostic_name(oDiagnostic):
    """The name of a slang diagnostic, such as WidthTruncate."""
    return str(oDiagnostic.code).replace("DiagCode(", "").rstrip(")")
