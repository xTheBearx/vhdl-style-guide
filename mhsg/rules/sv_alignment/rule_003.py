# -*- coding: utf-8 -*-

from mhsg.rules.sv_align import Rule
from mhsg.rules.sv_tree import elements


class rule_003(Rule):
    """
    This rule aligns the opening parentheses of the named parameter assignments of an instance in a column, as
    Verible's formatter does. By default it infers whether the author meant them aligned or flush left;
    **policy** set to align or flush_left forces one.

    **Violation**

    .. code-block:: systemverilog

       .Width(8),
       .Depth(16)

    **Fix**

    .. code-block:: systemverilog

       .Width(8),
       .Depth(16)
    """

    def __init__(self):
        super().__init__()
        self.minimum_spaces = 0
        self.solution = "Align the column"

    def alignment_groups(self, oFile):
        for oAssignment in oFile.nodes("ParameterValueAssignment"):
            yield [(o, o.openParen) if o.kind.name == "NamedParamAssignment" else None for o in elements(oAssignment.parameters)]
