# -*- coding: utf-8 -*-

from mhsg.rules.sv_lint.diagnostics import Rule


class rule_002(Rule):
    """
    This rule checks for latches: variables that combinational logic does not assign on every path.

    .. NOTE:: This is a lint rule. It runs in lint mode and reports what slang finds when it elaborates the file.

    **Violation**

    .. code-block:: systemverilog

       always_comb begin
           if (sel_i) y = a_i;
       end

    **Fix**

    .. code-block:: systemverilog

       always_comb begin
           y = '0;
           if (sel_i) y = a_i;
       end
    """

    def __init__(self):
        super().__init__()
        self.solution = "Assign the variable on every path"

    def accepts(self, sName):
        return sName == "InferredLatch"
