# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import source
from mhsg.rules.sv_tree import Problem, TreeRule, descendants, elements

NUMBERS = ("IntegerLiteralExpression", "RealLiteralExpression", "TimeLiteralExpression")


class rule_034(TreeRule, structure.Rule):
    """
    This rule checks for delays given as numbers in testbenches, modules without ports, as the STARC guide recommends
    (4.1.1.2): give testbench timing with parameters. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       initial #100 rst_n = 1'b1;

    **Fix**

    .. code-block:: systemverilog

       localparam int ResetTime = 100;
       initial #ResetTime rst_n = 1'b1;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oModule in oFile.nodes("ModuleDeclaration"):
            oPorts = oModule.header.ports
            if oPorts is not None and (not hasattr(oPorts, "ports") or list(elements(oPorts.ports))):
                continue
            for oDelay in descendants(oModule):
                if oDelay.kind.name != "DelayControl":
                    continue
                oValue = oDelay.delayValue
                while oValue is not None and oValue.kind.name == "ParenthesizedExpression":
                    oValue = oValue.expression
                if oValue is not None and oValue.kind.name in NUMBERS:
                    oToken = oFile.token_at(oDelay.getFirstToken())
                    if oToken is not None:
                        yield Problem(oToken, f"Give the delay {source(oValue)} with a parameter")
