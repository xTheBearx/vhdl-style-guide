# -*- coding: utf-8 -*-

from mhsg.rule_group import naming
from mhsg.rules.sv_nodes import declared_names, text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_014(TreeRule, naming.Rule):
    """
    This rule checks that the names of modules and ports do not end with an underscore, and that no name has two
    underscores in a row, as the STARC guide asks (1.1.1.6). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       module fifo_ (input logic clk__i);

    **Fix**

    .. code-block:: systemverilog

       module fifo (input logic clk_i);
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for sKind, oName in declared_names(oFile):
            sName = text(oName)
            oToken = oFile.token_at(oName)
            if oToken is None or not sName or sName.startswith("\\"):
                continue
            if "__" in sName:
                yield Problem(oToken, f"Rename {sName}, which has two underscores in a row")
            elif sKind in ("module", "port") and sName.endswith("_"):
                yield Problem(oToken, f"Rename {sName}, which ends with an underscore")
