# -*- coding: utf-8 -*-

from mhsg.rules.sv_lint.verilator_rule import Rule


class rule_012(Rule):
    """
    This rule reports signals assigned in more than one process (Verilator's MULTIDRIVEN), which synthesis
    resolves as multiple drivers. Verilator lints the SystemVerilog files of a run when it is installed, see
    sv_lint_011.

    .. NOTE:: This is a lint rule. It runs in lint mode and reports what Verilator finds; without Verilator it
       reports nothing.

    **Violation**

    .. code-block:: systemverilog

       always_ff @(posedge clk) busy <= 1'b1;
       always_ff @(posedge clk) if (done) busy <= 1'b0;

    **Fix**

    .. code-block:: systemverilog

       always_ff @(posedge clk) begin
           if (done) busy <= 1'b0;
           else busy <= 1'b1;
       end
    """

    def __init__(self):
        super().__init__(["MULTIDRIVEN"])
        self.solution = "Assign the signal in one process"
