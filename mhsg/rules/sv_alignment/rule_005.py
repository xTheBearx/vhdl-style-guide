# -*- coding: utf-8 -*-

from mhsg.rules.sv_align import Rule
from mhsg.rules.sv_alignment.items import BODIES, assignment_operator, row


class rule_005(Rule):
    """
    This rule aligns the assignment operators of consecutive continuous assignments and assignment statements in
    a column, as Verible's formatter does. By default it infers whether the author meant them aligned or flush
    left; **policy** set to align or flush_left forces one.

    **Violation**

    .. code-block:: systemverilog

       assign valid = valid_q;
       assign data_o = data_q;

    **Fix**

    .. code-block:: systemverilog

       assign valid  = valid_q;
       assign data_o = data_q;
    """

    def __init__(self):
        super().__init__()
        self.minimum_spaces = 1
        self.solution = "Align the column"

    def alignment_groups(self, oFile):
        for sKind, sField in BODIES.items():
            for oNode in oFile.nodes(sKind):
                yield [row(o, assignment_operator(o)) for o in getattr(oNode, sField, None) or []]
