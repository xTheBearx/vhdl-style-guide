# -*- coding: utf-8 -*-

from mhsg.rules.sv_lint.diagnostics import Rule


class rule_003(Rule):
    """
    This rule checks for variables driven by more than one process or continuous assignment.

    .. NOTE:: This is a lint rule. It runs in lint mode and reports what slang finds when it elaborates the file.

    **Violation**

    .. code-block:: systemverilog

       assign ready = 1'b0;
       always_ff @(posedge clk_i) ready <= 1'b1;

    **Fix**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i) ready <= 1'b1;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Drive the variable from one place"

    def accepts(self, sName):
        return "Multiple" in sName or sName == "MixedVarAssigns"
