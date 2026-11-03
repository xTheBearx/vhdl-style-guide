# -*- coding: utf-8 -*-

import re

from mhsg.rule_group import naming
from mhsg.rules.sv_nodes import names_of_kinds, text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_004(TreeRule, naming.Rule):
    """
    This rule checks that interface names match **pattern**, a regular expression, by default [a-z_0-9]+_if, as
    Verible's interface-name-style rule does.

    **Violation**

    .. code-block:: systemverilog

       interface Bus;

    **Fix**

    .. code-block:: systemverilog

       interface bus_if;
    """

    def __init__(self):
        super().__init__()
        self.solution = "See the rule documentation"
        self.pattern = "[a-z_0-9]+_if"
        self.configuration.append("pattern")

    def problems(self, oFile):
        for _, oName in names_of_kinds(oFile, ("interface",)):
            if not re.fullmatch(self.pattern, text(oName)):
                oToken = oFile.token_at(oName)
                if oToken is not None:
                    yield Problem(oToken, f"Rename {text(oName)} to match {self.pattern}")
