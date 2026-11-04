# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants, elements

LOGICAL = {"LogicalAndExpression": "LogicalOrExpression", "LogicalOrExpression": "LogicalAndExpression"}


class rule_012(TreeRule, structure.Rule):
    """
    This rule checks that && and || are not mixed without parentheses, as the STARC guide asks (2.10.1.2). It is
    disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       assign y = a && b || c;

    **Fix**

    .. code-block:: systemverilog

       assign y = (a && b) || c;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("LogicalAndExpression", "LogicalOrExpression"):
            for oOperand in (oNode.left, oNode.right):
                if oOperand is not None and oOperand.kind.name == LOGICAL[oNode.kind.name]:
                    oToken = oFile.token_at(oNode.operatorToken)
                    if oToken is not None:
                        yield Problem(oToken, "Parenthesize the mixed && and ||")
                    break
