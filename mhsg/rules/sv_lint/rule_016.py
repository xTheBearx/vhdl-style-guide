# -*- coding: utf-8 -*-

from mhsg.rules.sv_lint import diagnostics
from mhsg.rules.sv_lint.diagnostics import Rule


class rule_016(Rule):
    """
    This rule checks that macros used by several files of a run, the design-wide parameters, are defined in a file of
    their own, not in the file of a module, an interface or a program.

    .. NOTE:: This is a lint rule. It runs in lint mode, on the Verilog and SystemVerilog files of a run compiled
              together. It is disabled by default: a design need not follow it.

    A file of global parameters, included where they are used, shows what the whole design depends on, and changes in
    one place. A macro defined in the file of a module depends on the order the files are compiled in, and on that
    module being part of the design.

    **Violation**

    .. code-block:: systemverilog

       // fifo.sv
       `define BUS_WIDTH 32
       module fifo (...);

       // top.sv
       logic [`BUS_WIDTH - 1:0] data;

    **Fix**

    .. code-block:: systemverilog

       // global_parameters.svh
       `define BUS_WIDTH 32
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "Define the macro in a file of global parameters"

    def accepts(self, sName):
        return sName == diagnostics.GLOBAL_MACRO
