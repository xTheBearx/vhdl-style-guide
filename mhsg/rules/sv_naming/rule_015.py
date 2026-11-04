# -*- coding: utf-8 -*-

import re

from mhsg.rule_group import naming
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, elements


class rule_015(TreeRule, naming.Rule):
    """
    This rule checks that an instance is named after the module it instantiates, or after it and a number for
    several instances, such as fifo or fifo_1, as the STARC guide recommends (1.1.1.8). It is disabled by default; the
    starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       fifo buffer (.clk_i(clk_i));

    **Fix**

    .. code-block:: systemverilog

       fifo fifo (.clk_i(clk_i));
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("HierarchyInstantiation"):
            sModule = text(oNode.type)
            for oInstance in elements(oNode.instances):
                if oInstance.decl is None:
                    continue
                sName = text(oInstance.decl.name)
                if sName == sModule or re.fullmatch(re.escape(sModule) + r"_\d+", sName):
                    continue
                oToken = oFile.token_at(oInstance.decl.name)
                if oToken is not None:
                    yield Problem(oToken, f"Name the instance {sModule}, or {sModule}_<number>")
