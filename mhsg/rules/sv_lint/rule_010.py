# -*- coding: utf-8 -*-

from mhsg.rules.sv_lint.diagnostics import Rule
from mhsg.svFile.lint import UNDRIVEN


class rule_010(Rule):
    """
    This rule checks for variables, nets and output ports that nothing drives. A file that uses modules, packages
    or macros of other files is not checked, as a signal driven there would look undriven.

    .. NOTE:: This is a lint rule. It runs in lint mode and reports what slang finds when it elaborates the file.

    **Violation**

    .. code-block:: systemverilog

       module counter (output logic [7:0] count_o);
       endmodule

    **Fix**

    .. code-block:: systemverilog

       module counter (output logic [7:0] count_o);
           assign count_o = '0;
       endmodule
    """

    def __init__(self):
        super().__init__()
        self.solution = "Drive the signal or remove it"

    def accepts(self, sName):
        return sName in UNDRIVEN
