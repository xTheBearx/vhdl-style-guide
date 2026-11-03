# -*- coding: utf-8 -*-

from mhsg.rules.sv_lint.verilator_rule import Rule

# Verilator's warnings for checks slang does not make
DEFAULT_WARNINGS = (
    "ALWCOMBORDER",
    "BLKSEQ",
    "CASEX",
    "COMBDLY",
    "INITIALDLY",
    "SYNCASYNCNET",
)


class rule_011(Rule):
    """
    This rule reports the warnings of Verilator, when it is installed, for checks slang does not make: blocking
    assignments in clocked processes (BLKSEQ), non-blocking assignments in combinational ones (COMBDLY), and others.
    The verilator_warnings option lists the warnings reported, by Verilator's names; by default those whose checks
    slang does not make, but for MULTIDRIVEN and CASEINCOMPLETE, which sv_lint_012 and sv_lint_013 report.

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
        super().__init__(DEFAULT_WARNINGS)
        self.configuration.append("verilator_warnings")
