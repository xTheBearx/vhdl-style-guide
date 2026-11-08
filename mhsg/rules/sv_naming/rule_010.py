# -*- coding: utf-8 -*-

from mhsg.rule_group import naming
from mhsg.rules.sv_nodes import VHDL_KEYWORDS, declared_names, text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_010(TreeRule, naming.Rule):
    """
    This rule checks that no name is a VHDL keyword, in any case, as the STARC guide asks (1.1.1.3), so the
    design can be translated or mixed with VHDL. The keywords of the language of the file cannot be names. It is
    disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       logic signal;

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
            if text(oName).lower() in VHDL_KEYWORDS:
                oToken = oFile.token_at(oName)
                if oToken is not None:
                    yield Problem(oToken, f"Rename {text(oName)}, a VHDL keyword")
