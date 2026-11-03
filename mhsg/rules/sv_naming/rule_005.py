# -*- coding: utf-8 -*-

import re

from mhsg.rule_group import naming
from mhsg.rules.sv_nodes import names_of_kinds, text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_005(TreeRule, naming.Rule):
    """
    This rule checks that macro names match **pattern**, a regular expression, by default [A-Z_0-9]+, as
    Verible's macro-name-style rule does; macros whose names start with :code:`uvm_` or :code:`UVM_` may be
    lower case.

    **Violation**

    .. code-block:: systemverilog

       `define data_width 8

    **Fix**

    .. code-block:: systemverilog

       `define DATA_WIDTH 8
    """

    def __init__(self):
        super().__init__()
        self.solution = "See the rule documentation"
        self.pattern = "[A-Z_0-9]+"
        self.configuration.append("pattern")

    def problems(self, oFile):
        for _, oName in names_of_kinds(oFile, ("macro",)):
            sName = text(oName)
            if sName.lower().startswith("uvm_") and re.fullmatch("[a-zA-Z_0-9]+", sName):
                continue
            if not re.fullmatch(self.pattern, sName):
                oToken = oFile.token_at(oName)
                if oToken is not None:
                    yield Problem(oToken, f"Rename macro {sName} to match {self.pattern}")
