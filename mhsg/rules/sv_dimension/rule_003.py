# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import PACKED_TYPES, integer_of
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_003(TreeRule, structure.Rule):
    """
    This rule checks that the least significant bit of a packed dimension is 0, as the STARC guide asks (2.1.6.2),
    for dimensions whose bounds are numbers. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       logic [8:1] data;

    **Fix**

    .. code-block:: systemverilog

       logic [7:0] data;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oDimension in oFile.nodes("VariableDimension"):
            oParent = oDimension.parent
            if oParent is None or oParent.kind.name not in PACKED_TYPES:
                continue
            oRange = oDimension.specifier.selector if oDimension.specifier is not None else None
            if oRange is None or oRange.kind.name != "SimpleRangeSelect":
                continue
            iLeft, iRight = integer_of(oRange.left), integer_of(oRange.right)
            if iLeft is not None and iRight is not None and min(iLeft, iRight) != 0:
                oToken = oFile.token_at(oDimension.getFirstToken())
                if oToken is not None:
                    yield Problem(oToken, "Number the bits from 0")
