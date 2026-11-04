# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants, elements


class rule_003(TreeRule, structure.Rule):
    """
    This rule checks that a declaration names one signal, as the STARC guide recommends (3.1.3.4), so each can have
    its own comment. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       logic valid, ready;

    **Fix**

    .. code-block:: systemverilog

       logic valid;  // the data is valid
       logic ready;  // the sink takes the data
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("DataDeclaration", "NetDeclaration", "PortDeclaration"):
            lDeclarators = elements(oNode.declarators)
            if len(lDeclarators) > 1:
                oToken = oFile.token_at(lDeclarators[1].name)
                if oToken is not None:
                    yield Problem(oToken, "Declare one signal per declaration")
