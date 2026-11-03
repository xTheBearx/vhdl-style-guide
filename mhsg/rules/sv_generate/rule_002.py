# -*- coding: utf-8 -*-

import re

from mhsg.rule_group import structure
from mhsg.rules.sv_generate.blocks import generate_blocks, label_of
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_002(TreeRule, structure.Rule):
    """
    This rule checks that the labels of generate blocks match **pattern**, a regular expression, by default
    (g_|gen_).*, as Verible's generate-label-prefix rule does.

    **Violation**

    .. code-block:: systemverilog

       for (genvar i = 0; i < Depth; i++) begin : stage

    **Fix**

    .. code-block:: systemverilog

       for (genvar i = 0; i < Depth; i++) begin : gen_stage
    """

    def __init__(self):
        super().__init__()
        self.pattern = "(g_|gen_).*"
        self.configuration.append("pattern")
        self.solution = "Start the label of the generate block with gen_"

    def problems(self, oFile):
        for oBlock in generate_blocks(oFile):
            oLabel = label_of(oBlock)
            if oLabel is not None and not re.fullmatch(self.pattern, oLabel.rawText):
                oToken = oFile.token_at(oLabel)
                if oToken is not None:
                    yield Problem(oToken, f"Rename {oLabel.rawText} to match {self.pattern}")
