# -*- coding: utf-8 -*-

import os

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_005(TreeRule, structure.Rule):
    """
    This rule checks that the files an include directive names end in .h, .vh, .svh or .inc, as the STARC guide asks
    (1.1.4.1, 3.5.2.5). **extensions** lists the allowed extensions. It is disabled by default; the starc rule set
    enables it.

    **Violation**

    .. code-block:: systemverilog

       `include "definitions.v"

    **Fix**

    .. code-block:: systemverilog

       `include "definitions.vh"
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"
        self.extensions = [".h", ".vh", ".svh", ".inc"]
        self.configuration.append("extensions")

    def problems(self, oFile):
        lExtensions = [str(s).lower() for s in self.extensions]
        for oNode in oFile.nodes("IncludeDirective"):
            sName = text(oNode.fileName).strip('"<>')
            if os.path.splitext(sName)[1].lower() not in lExtensions:
                oToken = oFile.token_at(oNode.fileName)
                if oToken is not None:
                    yield Problem(oToken, f"Name the include file with one of the extensions {', '.join(lExtensions)}")
