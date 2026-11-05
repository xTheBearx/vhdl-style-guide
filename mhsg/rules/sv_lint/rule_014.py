# -*- coding: utf-8 -*-

from mhsg.rules.sv_lint import diagnostics
from mhsg.rules.sv_lint.diagnostics import Rule


class rule_014(Rule):
    """
    This rule checks that an instance that sets parameters of a module sets all of them.

    .. NOTE:: This is a lint rule. It runs in lint mode, on the SystemVerilog files of a run compiled together, and
              checks the instances of modules defined in the run. It is disabled by default: a design need not follow
              it.

    Each parameter the instance leaves out takes the default of the module, which can change with the module without
    the instance showing it. Parameters of the module that are local, localparam declarations and parameters of the
    body of a module with a parameter port list, cannot be set and are not counted.

    **Violation**

    .. code-block:: systemverilog

       fifo #(.WIDTH(8)) u_fifo (.clk_i(clk_i));

    **Fix**

    .. code-block:: systemverilog

       fifo #(.WIDTH(8), .DEPTH(16)) u_fifo (.clk_i(clk_i));
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "Set every parameter of the module in the instance"

    def accepts(self, sName):
        return sName == diagnostics.PARTIAL_OVERRIDE
