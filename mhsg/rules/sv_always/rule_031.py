# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_always.rule_012 import clock_events
from mhsg.rules.sv_always.rule_030 import read_before_assigned
from mhsg.rules.sv_tree import TreeRule


class rule_031(TreeRule, structure.Rule):
    """
    This rule checks that an edge triggered always block assigns each variable it writes with blocking assignments
    on every path before it reads it. It is disabled by default; the do254 rule set enables it (CP10), and the
    do254_plus rule set (VAR).

    Such a variable keeps its value from the previous clock edge, so synthesis makes it a register. That register is
    easy to overlook, because no nonblocking assignment shows it. Assign the variable before reading it, or make the
    register explicit with a nonblocking assignment.

    **Violation**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i) begin
           count = count + 1;
           count_o <= count;
       end

    **Fix**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i) begin
           count_q <= count_q + 1;
       end
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "Assign the variable before reading it, or make it a register"

    def problems(self, oFile):
        for oBlock in oFile.nodes("AlwaysBlock", "AlwaysFFBlock"):
            lClocks, _ = clock_events(oBlock)
            if lClocks:
                yield from read_before_assigned(
                    oFile,
                    oBlock.statement.statement,
                    True,
                    "{} keeps its value from the previous clock edge, a hidden register: assign it before reading it, or use a nonblocking assignment",
                )
