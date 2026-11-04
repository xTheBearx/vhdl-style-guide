# -*- coding: utf-8 -*-

import re

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_008(TreeRule, structure.Rule):
    """
    This rule checks for text macros used in the definition of other text macros, as the STARC guide recommends
    (3.2.2.5). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       `define DEPTH (`WIDTH * 2)

    **Fix**

    .. code-block:: systemverilog

       localparam int Depth = Width * 2;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("DefineDirective"):
            for oBody in oNode.body:
                if oBody.kind.name == "Directive" and re.fullmatch(r"`[A-Za-z_][A-Za-z0-9_$]*", oBody.rawText) and not oBody.rawText.startswith("`__"):
                    oToken = oFile.token_at(oNode.name)
                    if oToken is not None:
                        yield Problem(oToken, f"Do not use the macro {oBody.rawText} in the macro {text(oNode.name)}")
                    break
