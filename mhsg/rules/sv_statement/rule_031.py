# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import source
from mhsg.rules.sv_tree import Problem, TreeRule, descendants

PROCEDURAL = ("AlwaysBlock", "AlwaysFFBlock", "AlwaysCombBlock", "AlwaysLatchBlock", "InitialBlock")


class rule_031(TreeRule, structure.Rule):
    """
    This rule checks that a procedural block toggles at most one signal, with an assignment such as clk = ~clk, as
    the STARC guide recommends (4.1.7.1): generate each clock in a block of its own. It is disabled by default; the
    starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       always begin
           #5 clk_a = ~clk_a;
           #5 clk_b = ~clk_b;
       end

    **Fix**

    .. code-block:: systemverilog

       always #5 clk_a = ~clk_a;
       always #7 clk_b = ~clk_b;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oBlock in oFile.nodes(*PROCEDURAL):
            lToggled = []
            for oNode in descendants(oBlock):
                if oNode.kind.name not in ("AssignmentExpression", "NonblockingAssignmentExpression") or oNode.right is None:
                    continue
                oRight = oNode.right
                if oRight.kind.name in ("UnaryBitwiseNotExpression", "UnaryLogicalNotExpression") and source(oRight.operand) == source(oNode.left):
                    if source(oNode.left) not in [s for s, _ in lToggled]:
                        lToggled.append((source(oNode.left), oNode.left))
            lToggled.sort(key=lambda t: t[1].getFirstToken().location.offset)
            for _, oLeft in lToggled[1:]:
                oToken = oFile.token_at(oLeft.getFirstToken())
                if oToken is not None:
                    yield Problem(oToken, f"Generate the clock {source(oLeft)} in a block of its own")
