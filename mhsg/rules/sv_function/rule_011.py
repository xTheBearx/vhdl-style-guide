# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import inside
from mhsg.rules.sv_tree import Problem, TreeRule, elements


class rule_011(TreeRule, structure.Rule):
    """
    This rule checks that the if and case statements of a function cover every condition, with an else or a default,
    as the STARC guide asks (2.1.1.2). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       function automatic logic f(input logic a);
           if (a) f = 1'b1;
       endfunction

    **Fix**

    .. code-block:: systemverilog

       function automatic logic f(input logic a);
           if (a) f = 1'b1;
           else f = 1'b0;
       endfunction
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("ConditionalStatement"):
            if oNode.elseClause is None and inside(oNode, "FunctionDeclaration"):
                oToken = oFile.token_at(oNode.getFirstToken())
                if oToken is not None:
                    yield Problem(oToken, "Add an else to the if of the function")
        for oNode in oFile.nodes("CaseStatement"):
            if inside(oNode, "FunctionDeclaration") and not any(o.kind.name == "DefaultCaseItem" for o in elements(oNode.items)):
                oToken = oFile.token_at(oNode.caseKeyword)
                if oToken is not None:
                    yield Problem(oToken, "Add a default to the case of the function")
