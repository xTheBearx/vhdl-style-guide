# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_003(TreeRule, structure.Rule):
    """
    This rule checks that the ports of an instance are connected by name, never by position, as the STARC guide asks
    (3.2.3.1). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       fifo fifo (clk_i, data_i, data_o);

    **Fix**

    .. code-block:: systemverilog

       fifo fifo (.clk_i(clk_i), .data_i(data_i), .data_o(data_o));
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oInstance in oFile.nodes("HierarchicalInstance"):
            for oConnection in oInstance.connections:
                if hasattr(oConnection, "kind") and oConnection.kind.name == "OrderedPortConnection" and oConnection.expr is not None:
                    oToken = oFile.token_at(oInstance.getFirstToken())
                    if oToken is not None:
                        yield Problem(oToken, "Connect the ports by name")
                    break
