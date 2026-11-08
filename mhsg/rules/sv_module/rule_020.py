# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants


class rule_020(TreeRule, structure.Rule):
    """
    This rule checks for inout ports. It is disabled by default; the do254_plus rule set enables it (PORT).

    An inout port implies a tri-state driver and belongs only on the top level, for device pins. Justify the inout
    ports of the top level with a waiver.

    **Violation**

    .. code-block:: systemverilog

       module bus_ctrl (
           inout wire [7:0] data_io
       );

    **Fix**

    .. code-block:: systemverilog

       module bus_ctrl (
           input  logic [7:0] data_i,
           output logic [7:0] data_o,
           output logic       data_oe_o
       );
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "Use input and output ports"

    def problems(self, oFile):
        for oModule in oFile.nodes("ModuleDeclaration"):
            for oNode in descendants(oModule):
                if oNode.kind.name in ("VariablePortHeader", "NetPortHeader", "InterconnectPortHeader") and text(getattr(oNode, "direction", None)) == "inout":
                    oToken = oFile.token_at(oNode.direction)
                    if oToken is not None:
                        yield Problem(oToken, "Use inout ports only on the top level, for device pins")
