# -*- coding: utf-8 -*-

from mhsg import top_level
from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants


class rule_020(TreeRule, structure.Rule):
    """
    This rule checks for inout ports. It is disabled by default; the do254_plus rule set enables it (PORT).

    An inout port implies a tri-state driver and belongs only on the top level, for device pins, so the inout ports
    of the top level are not reported. The top level is the module the design section of the configuration names
    with top; without one, in lint mode with more than one file in the run or with index files given (--index_files
    or index_file_list), a module that no file of the run or of the index files instantiates. A file checked on
    its own without index files, a run outside lint mode and a file read from standard input do not show the design:
    without the design section, every inout port is reported.

    A testbench in the run instantiates the top level; name the top in the design section, so its pins are not
    reported.

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
            if top_level.is_top(oFile, oModule.header.name.valueText, True):
                continue
            for oNode in descendants(oModule):
                if oNode.kind.name in ("VariablePortHeader", "NetPortHeader", "InterconnectPortHeader") and text(getattr(oNode, "direction", None)) == "inout":
                    oToken = oFile.token_at(oNode.direction)
                    if oToken is not None:
                        yield Problem(oToken, "Use inout ports only on the top level, for device pins")
