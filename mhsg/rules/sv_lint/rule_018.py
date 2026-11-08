# -*- coding: utf-8 -*-

from mhsg.rules.sv_lint.diagnostics import Rule

# slang's warnings of an output port of an instance without a connection, or connected to nothing
UNCONNECTED_OUTPUTS = ("UnconnectedOutputPort", "EmptyOutputPortConn")


class rule_018(Rule):
    """
    This rule checks that every output port of an instance is connected. It implements DO-254 check CP12.

    .. NOTE:: This is a lint rule. It runs in lint mode and reports what slang finds when it elaborates the file.

    An output port that is missing from the connections of an instance, or connected to nothing, as .valid_o(), is
    not used. That is sometimes intended, for example for a debug output, and should then be justified with a waiver.

    **Violation**

    .. code-block:: systemverilog

       fifo u_fifo (
           .clk_i   (clk_i),
           .data_o  (data),
           .empty_o ()
       );

    **Fix**

    .. code-block:: systemverilog

       fifo u_fifo (
           .clk_i   (clk_i),
           .data_o  (data),
           .empty_o (empty)
       );
    """

    def __init__(self):
        super().__init__()
        self.solution = "Connect the output port, or justify leaving it open"

    def accepts(self, sName):
        return sName in UNCONNECTED_OUTPUTS
