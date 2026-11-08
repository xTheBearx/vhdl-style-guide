# -*- coding: utf-8 -*-

from mhsg import language
from mhsg.rules.sv_align import Rule
from mhsg.rules.sv_alignment.items import declared_name, row


class rule_008(Rule):
    """
    This rule aligns the names of the members of a struct or union in a column, as Verible's formatter does. By
    default it infers whether the author meant them aligned or flush left; **policy** set to align or flush_left
    forces one.

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
        # SystemVerilog only: it aligns the members of structs and unions, which Verilog-2005 does not have
        self.languages = (language.SYSTEMVERILOG,)
        self.minimum_spaces = 1
        self.solution = "Align the column"

    def alignment_groups(self, oFile):
        for oType in oFile.nodes("StructType", "UnionType"):
            yield [row(o, declared_name(o)) for o in oType.members]
