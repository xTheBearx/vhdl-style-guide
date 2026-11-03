# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import vector_literal
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_001(TreeRule, structure.Rule):
    """
    This rule checks that a sized binary literal has a digit for each bit, as Verible's
    undersized-binary-literal rule does; the fix adds leading zeros. Zero, as in 4'b0, is allowed.

    **Violation**

    .. code-block:: systemverilog

       assign mode = 4'b1;

    **Fix**

    .. code-block:: systemverilog

       assign mode = 4'b0001;
    """

    def __init__(self):
        super().__init__()
        self.fixable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("IntegerVectorExpression"):
            oLiteral = vector_literal(oNode)
            if oLiteral is None or oLiteral.base != "b" or oLiteral.size is None or oLiteral.value in (None, 0):
                continue
            if len(oLiteral.digits) < oLiteral.size:
                oToken = oFile.token_at(oNode.value)
                if oToken is not None:
                    yield Problem(oToken, f"Write all {oLiteral.size} digits of the binary literal", dAction={"digits": oLiteral.size})

    def _fix_violation(self, oViolation):
        oToken = oViolation.get_tokens()[0]
        sValue = oToken.get_value()
        iDigits = len(sValue.replace("_", ""))
        oToken.set_value("0" * (oViolation.get_action()["digits"] - iDigits) + sValue)
