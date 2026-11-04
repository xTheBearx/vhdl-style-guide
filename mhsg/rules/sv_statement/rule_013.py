# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule

PLAIN = ("IdentifierName", "IdentifierSelectName", "IntegerLiteralExpression", "IntegerVectorExpression", "ScopedName")


class rule_013(TreeRule, structure.Rule):
    """
    This rule checks that the operands of / and % are plain signals or constants, not expressions, as the STARC guide
    asks (2.10.8.1). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       assign y = (a + b) / c;

    **Fix**

    .. code-block:: systemverilog

       assign sum = a + b;
       assign y = sum / c;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("DivideExpression", "ModExpression"):
            for oOperand in (oNode.left, oNode.right):
                while oOperand is not None and oOperand.kind.name == "ParenthesizedExpression":
                    oOperand = oOperand.expression
                if oOperand is not None and oOperand.kind.name not in PLAIN:
                    oToken = oFile.token_at(oNode.operatorToken)
                    if oToken is not None:
                        yield Problem(oToken, "Divide signals, not expressions")
                    break
