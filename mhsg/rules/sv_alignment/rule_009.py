# -*- coding: utf-8 -*-

from mhsg.rules.sv_align import Rule
from mhsg.rules.sv_alignment.items import port_type
from mhsg.rules.sv_tree import elements


class rule_009(Rule):
    """
    This rule aligns the types of the port declarations of a module, interface or program header in a column after
    their directions, as Verible's formatter does. Ports without a type after their direction, such as input clk, are
    left out without ending the group. By default it infers whether the author meant them aligned or flush left;
    **policy** set to align or flush_left forces one.

    **Violation**

    .. code-block:: systemverilog

       module fifo (
           input logic clk_i,
           output logic [7:0] data_o
       );

    **Fix**

    .. code-block:: systemverilog

       module fifo (
           input  logic clk_i,
           output logic [7:0] data_o
       );
    """

    def __init__(self):
        super().__init__()
        self.solution = "Align the column"
        # The first column after the direction, before the packed dimensions and the names
        self.subphase = 2

    def alignment_groups(self, oFile):
        for oList in oFile.nodes("AnsiPortList"):
            yield [row_or_skip(o, port_type(o)) for o in elements(oList.ports)]


def row_or_skip(oItem, oTarget):
    """A row with the token to align; False, which keeps the group going, for an item with none."""
    return (oItem, oTarget) if oTarget is not None else False
