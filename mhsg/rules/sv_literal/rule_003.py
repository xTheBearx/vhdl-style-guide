# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule, elements


class rule_003(TreeRule, structure.Rule):
    """
    This rule checks that parameter values are written with an explicit base, such as 'd8, as the STARC guide
    asks (1.1.4.8). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       parameter int Depth = 8;

    **Fix**

    .. code-block:: systemverilog

       parameter int Depth = 'd8;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("ParameterDeclaration"):
            for oDeclarator in elements(oNode.declarators):
                oInitializer = oDeclarator.initializer
                if oInitializer is not None and oInitializer.expr.kind.name == "IntegerLiteralExpression":
                    oToken = oFile.token_at(oInitializer.expr.getFirstToken())
                    if oToken is not None:
                        yield Problem(oToken, "Write the parameter value with a base, such as 'd")
