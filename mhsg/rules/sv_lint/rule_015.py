# -*- coding: utf-8 -*-

from mhsg.rules.sv_lint import diagnostics
from mhsg.rules.sv_lint.diagnostics import Rule


class rule_015(Rule):
    """
    This rule checks that the parameters of a module are not named like parameters of another module of the run.

    .. NOTE:: This is a lint rule. It runs in lint mode, on the SystemVerilog files of a run compiled together. It is
              disabled by default: a design need not follow it.

    A name used for parameters of several modules is easily set in the wrong module, and a defparam or a search for
    the name finds them all. Parameters and localparam declarations are both checked; the first module of the run
    that declares a name keeps it.

    **Violation**

    .. code-block:: systemverilog

       module fifo #(parameter WIDTH = 8) (...);
       module top #(parameter WIDTH = 16) (...);

    **Fix**

    .. code-block:: systemverilog

       module fifo #(parameter FIFO_WIDTH = 8) (...);
       module top #(parameter TOP_WIDTH = 16) (...);
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "Give the parameter a name of its own"

    def accepts(self, sName):
        return sName == diagnostics.REUSED_PARAMETER
