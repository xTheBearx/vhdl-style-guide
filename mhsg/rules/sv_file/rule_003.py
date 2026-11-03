# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_003(TreeRule, structure.Rule):
    """
    This rule checks a file holds at most one module, as the STARC guide asks (1.1.1.1). It is disabled by
    default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       module fifo;
       endmodule
       module fifo_ram;
       endmodule

    **Fix**

    .. code-block:: systemverilog

       module fifo;
       endmodule
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oModule in oFile.nodes("ModuleDeclaration")[1:]:
            oToken = oFile.token_at(oModule.header.name)
            if oToken is not None:
                yield Problem(oToken, "Move the module to a file of its own")
