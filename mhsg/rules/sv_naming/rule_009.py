# -*- coding: utf-8 -*-

import re

from mhsg.rule_group import naming
from mhsg.rules.sv_nodes import declared_names, text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_009(TreeRule, naming.Rule):
    """
    This rule checks that names use only letters, digits and underscores and start with a letter, as the STARC
    guide asks (1.1.1.2): no escaped identifiers and no leading underscore. It is disabled by default; the starc
    rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       logic _valid;

    **Fix**

    .. code-block:: systemverilog

       logic valid;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for _, oName in declared_names(oFile):
            if not re.fullmatch("[A-Za-z][A-Za-z0-9_]*", text(oName)):
                oToken = oFile.token_at(oName)
                if oToken is not None:
                    yield Problem(oToken, f"Use only letters, digits and underscores in {text(oName)}, starting with a letter")
