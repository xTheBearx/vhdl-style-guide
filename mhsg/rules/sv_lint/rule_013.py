# -*- coding: utf-8 -*-

from mhsg.rules.sv_lint.verilator_rule import Rule


class rule_013(Rule):
    """
    This rule reports case statements that do not cover every value of their selector and have no default
    branch (Verilator's CASEINCOMPLETE). Verilator lints the Verilog and SystemVerilog files of a run when it is
    installed, see sv_lint_011.

    .. NOTE:: This is a lint rule. It runs in lint mode and reports what Verilator finds; without Verilator it
       reports nothing.

    **Violation**

    .. code-block:: systemverilog

       always_comb begin
           case (sel)
               2'b00: y = a;
               2'b01: y = b;
           endcase
       end

    **Fix**

    .. code-block:: systemverilog

       always_comb begin
           case (sel)
               2'b00: y = a;
               2'b01: y = b;
               default: y = '0;
           endcase
       end
    """

    def __init__(self):
        super().__init__(["CASEINCOMPLETE"])
        self.solution = "Cover every value of the selector, or add a default branch"
