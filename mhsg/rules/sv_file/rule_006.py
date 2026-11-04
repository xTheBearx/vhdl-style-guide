# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_006(TreeRule, structure.Rule):
    """
    This rule checks that a file holding modules declares their time unit, with a timescale directive or timeunit, as
    the STARC guide recommends (4.1.2.4). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       module fifo (input logic clk_i);

    **Fix**

    .. code-block:: systemverilog

       `timescale 1ns / 1ps
       module fifo (input logic clk_i);
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        lModules = oFile.nodes("ModuleDeclaration")
        if lModules and not oFile.nodes("TimeScaleDirective", "TimeUnitsDeclaration"):
            oToken = oFile.token_at(lModules[0].header.moduleKeyword)
            if oToken is not None:
                yield Problem(oToken, "Declare the time unit with `timescale or timeunit")
