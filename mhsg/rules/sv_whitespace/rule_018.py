# -*- coding: utf-8 -*-

from mhsg.rules.sv_spacing import Rule, kind, node

PORT_LISTS = ("AnsiPortList", "NonAnsiPortList")


class rule_018(Rule):
    """
    This rule checks for one space between the parenthesis closing the parameter list of a module, interface or
    program and the parenthesis opening its port list, as in ) (, as Verible's formatter does.

    **Violation**

    .. code-block:: systemverilog

       module fifo #(
           parameter int Depth = 4
       )(
           input logic clk_i
       );

    **Fix**

    .. code-block:: systemverilog

       module fifo #(
           parameter int Depth = 4
       ) (
           input logic clk_i
       );
    """

    def __init__(self):
        super().__init__()
        self.solution = "Put one space between ) and ("

    def spacing(self, oLeft, oRight):
        if kind(oLeft) == "CloseParenthesis" and node(oLeft) == "ParameterPortList" and kind(oRight) == "OpenParenthesis" and node(oRight) in PORT_LISTS:
            return (1, True)
        return None
