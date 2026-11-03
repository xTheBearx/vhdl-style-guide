# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_005(TreeRule, structure.Rule):
    """
    This rule checks for genvar declarations outside of a for loop; declare the genvar in the loop instead.

    **Violation**

    .. code-block:: systemverilog

       genvar i;
       for (i = 0; i < Depth; i++) begin : gen_stage

    **Fix**

    .. code-block:: systemverilog

       for (genvar i = 0; i < Depth; i++) begin : gen_stage
    """

    def __init__(self):
        super().__init__()
        self.solution = "Declare the genvar in the for loop"

    def problems(self, oFile):
        for oDeclaration in oFile.nodes("GenvarDeclaration"):
            oToken = oFile.token_at(oDeclaration.keyword)
            if oToken is not None:
                yield Problem(oToken, self.solution)
