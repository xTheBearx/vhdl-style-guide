# -*- coding: utf-8 -*-

import re

from mhsg.rule_group import naming
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_002(TreeRule, naming.Rule):
    """
    This rule checks that the names of enum types match **pattern**, a regular expression, by default
    [a-z_0-9]+(_t|_e), as Verible's enum-name-style rule does.

    **Violation**

    .. code-block:: systemverilog

       typedef enum logic {Idle, Busy} State;

    **Fix**

    .. code-block:: systemverilog

       typedef enum logic {Idle, Busy} state_e;
    """

    def __init__(self):
        super().__init__()
        self.solution = "See the rule documentation"
        self.pattern = "[a-z_0-9]+(_t|_e)"
        self.configuration.append("pattern")

    def problems(self, oFile):
        for oTypedef in oFile.nodes("TypedefDeclaration"):
            if oTypedef.type is not None and oTypedef.type.kind.name == "EnumType" and not re.fullmatch(self.pattern, text(oTypedef.name)):
                oToken = oFile.token_at(oTypedef.name)
                if oToken is not None:
                    yield Problem(oToken, f"Rename {text(oTypedef.name)} to match {self.pattern}")
