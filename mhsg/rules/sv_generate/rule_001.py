# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_generate.blocks import generate_blocks, label_of
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_001(TreeRule, structure.Rule):
    """
    This rule checks that the begin-end blocks of generate loops, ifs and cases are labelled.

    |unfixable|

    **Violation**

    .. code-block:: systemverilog

       for (genvar i = 0; i < Depth; i++) begin
           assign stage[i] = data_i;
       end

    **Fix**

    .. code-block:: systemverilog

       for (genvar i = 0; i < Depth; i++) begin : gen_stage
           assign stage[i] = data_i;
       end
    """

    def __init__(self):
        super().__init__()
        self.solution = "Label the generate block"

    def problems(self, oFile):
        for oBlock in generate_blocks(oFile):
            if label_of(oBlock) is None:
                oToken = oFile.token_at(oBlock.begin)
                if oToken is not None:
                    yield Problem(oToken, self.solution)
