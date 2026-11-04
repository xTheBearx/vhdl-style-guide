# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_lint.rule_008 import Subprogram
from mhsg.rules.sv_nodes import declared_names, text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants, elements

ASSIGNMENTS = ("AssignmentExpression", "NonblockingAssignmentExpression")


class rule_007(TreeRule, structure.Rule):
    """
    This rule checks that a function assigns only its own variables and its result, not the signals of the module, as
    the STARC guide asks (2.1.3.5). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       function automatic logic gate(input logic x);
           flag = x;
           gate = x;
       endfunction

    **Fix**

    Return the value and assign it where the function is called.

    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        setSignals = {text(oName) for sKind, oName in declared_names(oFile) if sKind in ("signal", "port")}
        for oNode in oFile.nodes("FunctionDeclaration"):
            oFunction = Subprogram(oNode)
            for oAssignment in descendants(oNode):
                if oAssignment.kind.name not in ASSIGNMENTS:
                    continue
                oFirst = oAssignment.left.getFirstToken()
                sName = text(oFirst)
                if sName in setSignals and sName not in oFunction.local:
                    oToken = oFile.token_at(oFirst)
                    if oToken is not None:
                        yield Problem(oToken, f"Do not assign {sName} in a function: return the value")
