# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_001(TreeRule, structure.Rule):
    """
    This rule checks for begin-end blocks directly in a module, outside of any generate construct.

    **Violation**

    .. code-block:: systemverilog

       module counter;
           begin : gen_count
               assign count = 1'b0;
           end
       endmodule

    **Fix**

    .. code-block:: systemverilog

       module counter;
           assign count = 1'b0;
       endmodule
    """

    def __init__(self):
        super().__init__()
        self.solution = "Remove the begin-end block from the module"

    def problems(self, oFile):
        for oBlock in oFile.nodes("GenerateBlock"):
            if oBlock.parent is not None and oBlock.parent.kind.name in ("ModuleDeclaration", "InterfaceDeclaration", "ProgramDeclaration"):
                oToken = oFile.token_at(oBlock.begin)
                if oToken is not None:
                    yield Problem(oToken, self.solution)
