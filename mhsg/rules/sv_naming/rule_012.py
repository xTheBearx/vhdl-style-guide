# -*- coding: utf-8 -*-

from mhsg.rule_group import naming
from mhsg.rules.sv_nodes import declared_names, text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_012(TreeRule, naming.Rule):
    """
    This rule checks that no two names of a file differ only in case, as the STARC guide asks (1.1.1.5). It is
    disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       logic data;
       logic Data;

    **Fix**

    .. code-block:: systemverilog

       logic data;
       logic data_q;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        dSeen = {}
        for _, oName in sorted(declared_names(oFile), key=lambda t: t[1].location.offset):
            sName = text(oName)
            sOther = dSeen.setdefault(sName.lower(), sName)
            if sOther != sName:
                oToken = oFile.token_at(oName)
                if oToken is not None:
                    yield Problem(oToken, f"Rename {sName}, which differs from {sOther} only in case")
