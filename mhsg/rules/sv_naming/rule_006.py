# -*- coding: utf-8 -*-

import re

from mhsg import language
from mhsg.rule_group import naming
from mhsg.rules.sv_nodes import names_of_kinds, text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_006(TreeRule, naming.Rule):
    """
    This rule checks that constraint names match **pattern**, a regular expression, by default ([a-z0-9]+_)+c,
    as Verible's constraint-name-style rule does.

    **Violation**

    .. code-block:: systemverilog

       constraint Length { length < 64; }

    **Fix**

    .. code-block:: systemverilog

       constraint length_c { length < 64; }
    """

    def __init__(self):
        super().__init__()
        # SystemVerilog only: it checks constraints, which Verilog-2005 does not have
        self.languages = (language.SYSTEMVERILOG,)
        self.solution = "See the rule documentation"
        self.pattern = "([a-z0-9]+_)+c"
        self.configuration.append("pattern")

    def problems(self, oFile):
        for _, oName in names_of_kinds(oFile, ("constraint",)):
            if not re.fullmatch(self.pattern, text(oName)):
                oToken = oFile.token_at(oName)
                if oToken is not None:
                    yield Problem(oToken, f"Rename {text(oName)} to match {self.pattern}")
