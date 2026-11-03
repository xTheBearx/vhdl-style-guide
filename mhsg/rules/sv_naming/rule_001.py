# -*- coding: utf-8 -*-

import re

from mhsg.rule_group import naming
from mhsg.rules.sv_nodes import names_of_kinds, text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_001(TreeRule, naming.Rule):
    """
    This rule checks that parameter names match **parameter_pattern** and localparam names match
    **localparam_pattern**, regular expressions, by default UpperCamelCase or ALL_CAPS for parameters and
    UpperCamelCase for localparams, as Verible's parameter-name-style rule does.

    **Violation**

    .. code-block:: systemverilog

       parameter int data_width = 8;

    **Fix**

    .. code-block:: systemverilog

       parameter int DataWidth = 8;
    """

    def __init__(self):
        super().__init__()
        self.solution = "See the rule documentation"
        self.parameter_pattern = "([A-Z0-9]+[a-z0-9]*)+(_[0-9]+)?|[A-Z_0-9]+"
        self.configuration.append("parameter_pattern")
        self.localparam_pattern = "([A-Z0-9]+[a-z0-9]*)+(_[0-9]+)?"
        self.configuration.append("localparam_pattern")

    def problems(self, oFile):
        for sCategory, oName in names_of_kinds(oFile, ("parameter", "localparam")):
            sPattern = self.parameter_pattern if sCategory == "parameter" else self.localparam_pattern
            if not re.fullmatch(sPattern, text(oName)):
                oToken = oFile.token_at(oName)
                if oToken is not None:
                    yield Problem(oToken, f"Rename {sCategory} {text(oName)} to match {sPattern}")
