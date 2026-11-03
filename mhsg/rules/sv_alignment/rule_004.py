# -*- coding: utf-8 -*-

from mhsg.rules.sv_align import Rule
from mhsg.rules.sv_alignment.items import BODIES, declared_name, row


class rule_004(Rule):
    """
    This rule aligns the names of consecutive variable and net declarations in a column, as Verible's formatter
    does. By default it infers whether the author meant them aligned or flush left; **policy** set to align or
    flush_left forces one.

    **Violation**

    .. code-block:: systemverilog

       logic valid;
       logic [7:0] data;

    **Fix**

    .. code-block:: systemverilog

       logic       valid;
       logic [7:0] data;
    """

    def __init__(self):
        super().__init__()
        self.minimum_spaces = 1
        self.solution = "Align the column"

    def alignment_groups(self, oFile):
        for sKind, sField in BODIES.items():
            for oNode in oFile.nodes(sKind):
                yield [row(o, declared_name(o)) for o in getattr(oNode, sField, None) or []]
