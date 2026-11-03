# -*- coding: utf-8 -*-

from mhsg.rule_group import naming
from mhsg.rules.sv_nodes import declared_names, text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_013(TreeRule, naming.Rule):
    """
    This rule checks the length of names, as the STARC guide asks: modules and instances **module_minimum** to
    **module_maximum** characters, 2 to 32 by default (1.1.2.1); other names **minimum** to **maximum**, 2 to 40
    by default (1.1.3.3). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       logic v;

    **Fix**

    .. code-block:: systemverilog

       logic valid;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"
        self.module_minimum = 2
        self.configuration.append("module_minimum")
        self.module_maximum = 32
        self.configuration.append("module_maximum")
        self.minimum = 2
        self.configuration.append("minimum")
        self.maximum = 40
        self.configuration.append("maximum")

    def problems(self, oFile):
        for sCategory, oName in declared_names(oFile):
            if sCategory in ("genvar",):
                continue
            if sCategory in ("module", "instance"):
                iMinimum, iMaximum = int(self.module_minimum), int(self.module_maximum)
            else:
                iMinimum, iMaximum = int(self.minimum), int(self.maximum)
            if not iMinimum <= len(text(oName)) <= iMaximum:
                oToken = oFile.token_at(oName)
                if oToken is not None:
                    yield Problem(oToken, f"Use {iMinimum} to {iMaximum} characters for {sCategory} {text(oName)}")
