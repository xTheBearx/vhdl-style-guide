# -*- coding: utf-8 -*-

from mhsg.rules.sv_lint.diagnostics import Rule

# slang's warnings of an input, inout or ref port of an instance without a connection, or connected to nothing
UNCONNECTED_INPUTS = (
    "UnconnectedInputPort",
    "UnconnectedInOutPort",
    "UnconnectedUnnamedPort",
    "EmptyInputPortConn",
    "EmptyInputPortConnDefault",
    "EmptyInOutPortConn",
    "RefPortUnconnected",
    "RefPortUnnamedUnconnected",
)


class rule_017(Rule):
    """
    This rule checks that every input and inout port of an instance is connected. It implements DO-254 check CP11.

    .. NOTE:: This is a lint rule. It runs in lint mode and reports what slang finds when it elaborates the file.

    An input port that is missing from the connections of an instance, or connected to nothing, as .addr(), floats or
    takes its default value. Ports of modules slang does not know, from files outside the run, are not checked.

    **Violation**

    .. code-block:: systemverilog

       fifo u_fifo (
           .clk_i  (clk_i),
           .data_i (),
           .data_o (data)
       );

    **Fix**

    .. code-block:: systemverilog

       fifo u_fifo (
           .clk_i  (clk_i),
           .data_i (payload),
           .data_o (data)
       );
    """

    def __init__(self):
        super().__init__()
        self.solution = "Connect the input port"

    def accepts(self, sName):
        return sName in UNCONNECTED_INPUTS
