# -*- coding: utf-8 -*-

import re

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_004(TreeRule, structure.Rule):
    """
    This rule checks that include directives name files by relative paths, as the STARC guide asks (3.2.2.4). It
    is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       `include "/home/user/rtl/defines.svh"

    **Fix**

    .. code-block:: systemverilog

       `include "defines.svh"
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("IncludeDirective"):
            sName = text(oNode.fileName).strip('"<>')
            if sName.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", sName):
                oToken = oFile.token_at(oNode.fileName)
                if oToken is not None:
                    yield Problem(oToken, "Use a relative path in `include")
