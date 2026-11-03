# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_003(TreeRule, structure.Rule):
    """
    This rule checks for begin-end blocks directly in a generate region, a Verilog-2001 form.

    |unfixable|

    **Violation**

    .. code-block:: systemverilog

       generate
           begin : gen_logic
               assign valid = 1'b1;
           end
       endgenerate

    **Fix**

    .. code-block:: systemverilog

       assign valid = 1'b1;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Remove the begin-end block of the generate region"

    def problems(self, oFile):
        for oBlock in oFile.nodes("GenerateBlock"):
            if oBlock.parent is not None and oBlock.parent.kind.name == "GenerateRegion":
                oToken = oFile.token_at(oBlock.begin)
                if oToken is not None:
                    yield Problem(oToken, self.solution)
