# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import vector_literal
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_002(TreeRule, structure.Rule):
    """
    This rule checks that the value of a sized literal fits its width, as Verible's truncated-numeric-literal
    rule does.

    **Violation**

    .. code-block:: systemverilog

       assign mask = 4'hFF;

    **Fix**

    .. code-block:: systemverilog

       assign mask = 8'hFF;
    """

    def __init__(self):
        super().__init__()
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("IntegerVectorExpression"):
            oLiteral = vector_literal(oNode)
            if oLiteral is None or oLiteral.size is None or oLiteral.value is None:
                continue
            if oLiteral.bits() > oLiteral.size:
                oToken = oFile.token_at(oNode.getFirstToken())
                if oToken is not None:
                    yield Problem(oToken, f"The value needs {oLiteral.bits()} bits, more than the width {oLiteral.size}")
