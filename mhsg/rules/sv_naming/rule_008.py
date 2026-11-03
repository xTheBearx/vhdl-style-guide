# -*- coding: utf-8 -*-

import re

from mhsg.rule_group import naming
from mhsg.rules.sv_nodes import names_of_kinds, text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_008(TreeRule, naming.Rule):
    """
    This rule checks that the names of signals and ports match **pattern**, a regular expression, by default
    lower_snake_case [a-z_0-9]+, as Verible's signal-name-style rule does. It is disabled by default, as in
    Verible.

    **Violation**

    .. code-block:: systemverilog

       logic DataValid;

    **Fix**

    .. code-block:: systemverilog

       logic data_valid;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"
        self.pattern = "[a-z_0-9]+"
        self.configuration.append("pattern")

    def problems(self, oFile):
        for _, oName in names_of_kinds(oFile, ("signal", "port")):
            if not re.fullmatch(self.pattern, text(oName)):
                oToken = oFile.token_at(oName)
                if oToken is not None:
                    yield Problem(oToken, f"Rename {text(oName)} to match {self.pattern}")
