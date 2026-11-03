# -*- coding: utf-8 -*-

from mhsg.rules.sv_align import Rule
from mhsg.rules.sv_tree import elements


class rule_002(Rule):
    """
    This rule aligns the opening parentheses of the named port connections of an instance in a column, as
    Verible's formatter does. By default it infers whether the author meant them aligned or flush left;
    **policy** set to align or flush_left forces one.

    **Violation**

    .. code-block:: systemverilog

       .clk_i(clk_i),
       .data_i(data)

    **Fix**

    .. code-block:: systemverilog

       .clk_i (clk_i),
       .data_i(data)
    """

    def __init__(self):
        super().__init__()
        self.minimum_spaces = 0
        self.solution = "Align the column"

    def alignment_groups(self, oFile):
        for oInstance in oFile.nodes("HierarchicalInstance"):
            yield [(o, o.openParen) if o.kind.name == "NamedPortConnection" and o.openParen.rawText else None for o in elements(oInstance.connections)]
