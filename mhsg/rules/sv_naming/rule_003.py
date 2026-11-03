# -*- coding: utf-8 -*-

import re

from mhsg.rule_group import naming
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_003(TreeRule, naming.Rule):
    """
    This rule checks that the names of struct and union types match **pattern**, a regular expression, by
    default [a-z_0-9]+_t, as Verible's struct-union-name-style rule does.

    **Violation**

    .. code-block:: systemverilog

       typedef struct packed {logic a;} Beat;

    **Fix**

    .. code-block:: systemverilog

       typedef struct packed {logic a;} beat_t;
    """

    def __init__(self):
        super().__init__()
        self.solution = "See the rule documentation"
        self.pattern = "[a-z_0-9]+_t"
        self.configuration.append("pattern")

    def problems(self, oFile):
        for oTypedef in oFile.nodes("TypedefDeclaration"):
            if oTypedef.type is not None and oTypedef.type.kind.name in ("StructType", "UnionType") and not re.fullmatch(self.pattern, text(oTypedef.name)):
                oToken = oFile.token_at(oTypedef.name)
                if oToken is not None:
                    yield Problem(oToken, f"Rename {text(oTypedef.name)} to match {self.pattern}")
