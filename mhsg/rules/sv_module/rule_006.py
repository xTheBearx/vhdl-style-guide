# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_006(TreeRule, structure.Rule):
    """
    This rule checks for text macros that define a constant, such as `define WIDTH 8, as the STARC guide asks
    (3.2.2.7): use a parameter. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       `define WIDTH 8

    **Fix**

    .. code-block:: systemverilog

       localparam int Width = 8;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("DefineDirective"):
            lBody = list(oNode.body)
            if (
                oNode.formalArguments is None
                and len(lBody) == 1
                and lBody[0].kind.name in ("IntegerLiteral", "IntegerBase", "RealLiteral", "UnbasedUnsizedLiteral")
            ):
                oToken = oFile.token_at(oNode.name)
                if oToken is not None:
                    yield Problem(oToken, f"Use a parameter for the constant {text(oNode.name)}")
