# -*- coding: utf-8 -*-

from mhsg.rules.sv_align import Rule
from mhsg.rules.sv_tree import elements


class rule_001(Rule):
    """
    This rule aligns the names of the port declarations of a module, interface or program header in a column, as
    Verible's formatter does. By default it infers whether the author meant them aligned or flush left;
    **policy** set to align or flush_left forces one.

    **Violation**

    .. code-block:: systemverilog

       input logic clk_i,
       output logic [7:0] data_o

    **Fix**

    .. code-block:: systemverilog

       input  logic       clk_i,
       output logic [7:0] data_o
    """

    def __init__(self):
        super().__init__()
        self.minimum_spaces = 1
        self.solution = "Align the column"

    def alignment_groups(self, oFile):
        for oList in oFile.nodes("AnsiPortList"):
            yield [(o, o.declarator.name) if o.kind.name == "ImplicitAnsiPort" and o.declarator is not None else None for o in elements(oList.ports)]
