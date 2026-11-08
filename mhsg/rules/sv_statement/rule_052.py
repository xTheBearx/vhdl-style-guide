# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_flow import reads
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, elements


class rule_052(TreeRule, structure.Rule):
    """
    This rule checks for combinational feedback in continuous assignments: a signal assigned from an expression that
    reads the signal itself. It is disabled by default; the do254 rule set enables it (SS3), with sv_always_030 for
    always blocks.

    Such a signal forms a loop without a register, whose behaviour is unpredictable. Assignments to an element or a
    slice, such as assign p[3:1] = p[2:0], are not checked, since they may read other elements. Loops through several
    assignments are found by design analysis (design_003).

    **Violation**

    .. code-block:: systemverilog

       assign hold = hold | pulse;

    **Fix**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i) begin
           hold_q <= hold_q | pulse;
       end
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "Break the combinational loop with a register"

    def problems(self, oFile):
        for oAssign in oFile.nodes("ContinuousAssign"):
            for oAssignment in elements(oAssign.assignments):
                oLeft = getattr(oAssignment, "left", None)
                if oLeft is None or oLeft.kind.name != "IdentifierName":
                    continue
                sName = text(oLeft.identifier)
                if any(text(o.identifier) == sName for o in reads(oAssignment.right)):
                    oToken = oFile.token_at(oLeft.getFirstToken())
                    if oToken is not None:
                        yield Problem(oToken, f"{sName} is assigned from itself, a combinational loop")
