# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import inside
from mhsg.rules.sv_tree import Problem, TreeRule, descendants


class rule_004(TreeRule, structure.Rule):
    """
    This rule checks for nonblocking assignments (<=) in functions, as the STARC guide asks (2.1.2.2). Methods
    of classes, such as the drivers of a testbench writing to a virtual interface, are not checked.

    **Violation**

    .. code-block:: systemverilog

       function automatic logic f(input logic a);
           f <= a;

    **Fix**

    .. code-block:: systemverilog

       function automatic logic f(input logic a);
           f = a;
    """

    def __init__(self):
        super().__init__()
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oFunction in oFile.nodes("FunctionDeclaration"):
            if inside(oFunction, "ClassDeclaration"):
                continue
            for oNode in descendants(oFunction):
                if oNode.kind.name == "NonblockingAssignmentExpression":
                    oToken = oFile.token_at(oNode.operatorToken)
                    if oToken is not None:
                        yield Problem(oToken, "Use a blocking assignment (=) in a function")
