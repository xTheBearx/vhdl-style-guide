# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import source
from mhsg.rules.sv_tree import Problem, TreeRule, descendants

ARITHMETIC = ("AddExpression", "SubtractExpression", "MultiplyExpression", "DivideExpression", "ModExpression", "PowerExpression")


class rule_048(TreeRule, structure.Rule):
    """
    This rule checks for an arithmetic expression that both branches of an if and else compute, as the STARC guide
    recommends (2.10.7.2): compute it once, before the if. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       if (sel) y = a + b;
       else z = a + b;

    **Fix**

    .. code-block:: systemverilog

       assign sum = a + b;
       if (sel) y = sum;
       else z = sum;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oIf in oFile.nodes("ConditionalStatement"):
            if oIf.elseClause is None:
                continue
            dThen = expressions(oIf.statement)
            for sText, oNode in expressions(oIf.elseClause.clause).items():
                if sText in dThen:
                    oToken = oFile.token_at(oNode.getFirstToken())
                    if oToken is not None:
                        yield Problem(oToken, f"Compute {source(oNode)} once, before the if")
                    break


def expressions(oStatement):
    """{text: node} of the outermost arithmetic expressions under a statement."""
    dReturn = {}
    for oNode in [oStatement, *descendants(oStatement)]:
        if oNode.kind.name in ARITHMETIC and (oNode.parent is None or oNode.parent.kind.name not in ARITHMETIC):
            dReturn.setdefault("".join(source(oNode).split()), oNode)
    return dReturn
