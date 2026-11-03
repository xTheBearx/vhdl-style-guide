# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import PACKED_TYPES, integer_of
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_001(TreeRule, structure.Rule):
    """
    This rule checks that packed dimensions are written from the most to the least significant bit, such as
    [7:0], as Verible's packed-dimensions-range-ordering rule does.

    **Violation**

    .. code-block:: systemverilog

       logic [0:7] data;

    **Fix**

    .. code-block:: systemverilog

       logic [7:0] data;
    """

    def __init__(self):
        super().__init__()
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oDimension in oFile.nodes("VariableDimension"):
            if oDimension.parent is None or oDimension.parent.kind.name not in PACKED_TYPES:
                continue
            oRange = oDimension.specifier.selector if oDimension.specifier is not None and oDimension.specifier.kind.name == "RangeDimensionSpecifier" else None
            if oRange is None or oRange.kind.name != "SimpleRangeSelect":
                continue
            iLeft, iRight = integer_of(oRange.left), integer_of(oRange.right)
            if (iLeft is not None and iRight is not None and iLeft < iRight) or (iLeft == 0 and iRight is None):
                oToken = oFile.token_at(oDimension.openBracket)
                if oToken is not None:
                    yield Problem(oToken, "Write the packed dimension as [msb:lsb]")
