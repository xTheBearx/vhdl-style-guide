# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import integer_of
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_002(TreeRule, structure.Rule):
    """
    This rule checks that unpacked dimensions are written as [0:N-1] or [N], as Verible's
    unpacked-dimensions-range-ordering rule does.

    **Violation**

    .. code-block:: systemverilog

       logic [7:0] mem [15:0];

    **Fix**

    .. code-block:: systemverilog

       logic [7:0] mem [16];
    """

    def __init__(self):
        super().__init__()
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oDimension in oFile.nodes("VariableDimension"):
            if oDimension.parent is None or oDimension.parent.kind.name != "Declarator":
                continue
            oRange = oDimension.specifier.selector if oDimension.specifier is not None and oDimension.specifier.kind.name == "RangeDimensionSpecifier" else None
            if oRange is None or oRange.kind.name != "SimpleRangeSelect":
                continue
            iLeft, iRight = integer_of(oRange.left), integer_of(oRange.right)
            if (iLeft is not None and iRight is not None and iLeft > iRight) or (iRight == 0 and iLeft is None):
                oToken = oFile.token_at(oDimension.openBracket)
                if oToken is not None:
                    yield Problem(oToken, "Write the unpacked dimension as [0:N-1] or [N]")
