# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_always.rule_003 import id_of
from mhsg.rules.sv_tree import Problem, TreeRule, descendants, elements

ALWAYS = ("AlwaysBlock", "AlwaysFFBlock", "AlwaysCombBlock", "AlwaysLatchBlock")


class rule_004(TreeRule, structure.Rule):
    """
    This rule checks that an always block does not mix blocking (=) and nonblocking (<=) assignments.
    Assignments in the header of a for loop are not counted.

    **Violation**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i) begin
           count_q <= count_d;
           valid_q = valid_d;
       end

    **Fix**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i) begin
           count_q <= count_d;
           valid_q <= valid_d;
       end
    """

    def __init__(self):
        super().__init__()
        self.solution = "Do not mix blocking and nonblocking assignments in an always block"

    def problems(self, oFile):
        for oBlock in oFile.nodes(*ALWAYS):
            lNodes = list(descendants(oBlock))
            sLoopHeaders = set()
            for oNode in lNodes:
                if oNode.kind.name == "ForLoopStatement":
                    for oPart in elements(oNode.initializers) + elements(oNode.steps):
                        sLoopHeaders.add(id_of(oPart))
            lBlocking = [o for o in lNodes if o.kind.name == "AssignmentExpression" and id_of(o) not in sLoopHeaders]
            lNonblocking = [o for o in lNodes if o.kind.name == "NonblockingAssignmentExpression"]
            if lBlocking and lNonblocking:
                oToken = oFile.token_at(oBlock.keyword)
                if oToken is not None:
                    yield Problem(oToken, self.solution)
