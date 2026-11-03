# -*- coding: utf-8 -*-

from mhsg.rules.sv_lint.diagnostics import Rule

# Verilator's warnings for checks slang does not make
DEFAULT_WARNINGS = (
    "ALWCOMBORDER",
    "BLKSEQ",
    "CASEINCOMPLETE",
    "CASEX",
    "COMBDLY",
    "INITIALDLY",
    "MULTIDRIVEN",
    "SYNCASYNCNET",
)


class rule_011(Rule):
    """
    This rule reports the warnings of Verilator, when it is installed, for checks slang does not make: blocking
    assignments in clocked processes (BLKSEQ), non-blocking assignments in combinational ones (COMBDLY), signals
    assigned in more than one process (MULTIDRIVEN), case statements that do not cover every value
    (CASEINCOMPLETE), and others. The verilator_warnings option lists the warnings reported, by Verilator's names;
    by default those whose checks slang does not make.

    Verilator lints the SystemVerilog files of a run together; the systemverilog section of the configuration turns
    it off with :code:`verilator: false`, or names the program with :code:`verilator: /path/to/verilator`.

    .. NOTE:: This is a lint rule. It runs in lint mode and reports what Verilator finds; without Verilator it
       reports nothing.

    **Violation**

    .. code-block:: systemverilog

       always_ff @(posedge clk) begin
           count = count + 1;
       end

    **Fix**

    .. code-block:: systemverilog

       always_ff @(posedge clk) begin
           count <= count + 1;
       end
    """

    def __init__(self):
        super().__init__()
        self.solution = "See Verilator's description of the warning"
        self.verilator_warnings = list(DEFAULT_WARNINGS)
        self.configuration.append("verilator_warnings")

    def accepts(self, sName):
        return sName.startswith("verilator.") and sName.split(".", 1)[1] in [str(s).upper() for s in self.verilator_warnings]

    def message(self, oDiagnostic):
        return f"{super().message(oDiagnostic)} (Verilator {oDiagnostic.name.split('.', 1)[1]})"
