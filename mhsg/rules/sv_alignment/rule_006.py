# -*- coding: utf-8 -*-

from mhsg.rules.sv_align import Rule
from mhsg.rules.sv_alignment.items import BODIES, parameter_equals, row
from mhsg.rules.sv_tree import elements


class rule_006(Rule):
    """
    This rule aligns the = of consecutive parameter and localparam declarations, and of the parameters of a
    header in a column, as Verible's formatter does. By default it infers whether the author meant them aligned
    or flush left; **policy** set to align or flush_left forces one.

    **Violation**

    .. code-block:: systemverilog

       localparam int Depth = 16;
       localparam int AddrWidth = 4;

    **Fix**

    .. code-block:: systemverilog

       localparam int Depth     = 16;
       localparam int AddrWidth = 4;
    """

    def __init__(self):
        super().__init__()
        self.minimum_spaces = 1
        self.solution = "Align the column"

    def alignment_groups(self, oFile):
        for sKind, sField in BODIES.items():
            for oNode in oFile.nodes(sKind):
                yield [row(o, parameter_equals(o)) for o in getattr(oNode, sField, None) or []]
        for oList in oFile.nodes("ParameterPortList"):
            yield [row(o, parameter_equals(o)) for o in elements(oList.declarations)]
