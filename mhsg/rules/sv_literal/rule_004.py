# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import integer_of, vector_literal
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_004(TreeRule, structure.Rule):
    """
    This rule checks that a literal whose value needs more than 32 bits has an explicit width, as the STARC
    guide asks (1.1.4.9). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       assign seed = 'h1_0000_0000;

    **Fix**

    .. code-block:: systemverilog

       assign seed = 33'h1_0000_0000;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("IntegerVectorExpression", "IntegerLiteralExpression"):
            if oNode.kind.name == "IntegerVectorExpression":
                oLiteral = vector_literal(oNode)
                if oLiteral is None or oLiteral.size is not None or oLiteral.value is None:
                    continue
                iValue = oLiteral.value
            else:
                if oNode.parent is not None and oNode.parent.kind.name == "IntegerVectorExpression":
                    continue
                iValue = integer_of(oNode)
            if iValue is not None and iValue.bit_length() > 32:
                oToken = oFile.token_at(oNode.getFirstToken())
                if oToken is not None:
                    yield Problem(oToken, "Give the literal a width; it needs more than 32 bits")
