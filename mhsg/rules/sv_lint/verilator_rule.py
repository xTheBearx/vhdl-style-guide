# -*- coding: utf-8 -*-
"""Base class of the lint rules that report Verilator's warnings, see mhsg/svFile/verilator.py."""

from mhsg.rules.sv_lint.diagnostics import Rule as DiagnosticRule


class Rule(DiagnosticRule):
    """Reports the Verilator warnings of the codes in self.verilator_warnings, with Verilator's message."""

    def __init__(self, lWarnings):
        super().__init__()
        self.solution = "See Verilator's description of the warning"
        self.verilator_warnings = list(lWarnings)

    def accepts(self, sName):
        return sName.startswith("verilator.") and sName.split(".", 1)[1] in [str(s).upper() for s in self.verilator_warnings]

    def message(self, oDiagnostic):
        return f"{super().message(oDiagnostic)} (Verilator {oDiagnostic.name.split('.', 1)[1]})"


# The rules that report Verilator's warnings; Verilator runs when one of them is enabled
RULES = ("sv_lint_011", "sv_lint_012", "sv_lint_013")
