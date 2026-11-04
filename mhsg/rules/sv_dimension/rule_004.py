# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import integer_of
from mhsg.rules.sv_tree import Problem, TreeRule, elements


class rule_004(TreeRule, structure.Rule):
    """
    This rule checks that the packed dimensions of ports are written with parameters, not numbers, as the STARC guide
    recommends (1.1.4.7, 3.1.5.1, 3.1.5.2), so the module can be reused with other widths. It is disabled by default;
    the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       module fifo (input logic [7:0] data_i);

    **Fix**

    .. code-block:: systemverilog

       module fifo #(parameter int Width = 8) (input logic [Width-1:0] data_i);
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oPort in oFile.nodes("ImplicitAnsiPort"):
            oType = getattr(oPort.header, "dataType", None) if oPort.header is not None else None
            for oDimension in elements(getattr(oType, "dimensions", None) or []):
                oRange = oDimension.specifier.selector if oDimension.specifier is not None else None
                if oRange is None or oRange.kind.name != "SimpleRangeSelect":
                    continue
                iLeft, iRight = integer_of(oRange.left), integer_of(oRange.right)
                if iLeft is not None and iRight is not None and max(iLeft, iRight) > 0:
                    oToken = oFile.token_at(oDimension.getFirstToken())
                    if oToken is not None:
                        yield Problem(oToken, "Write the width of the port with a parameter")
