# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule, descendants


class rule_007(TreeRule, structure.Rule):
    """
    This rule checks for conditional operators nested in the branches of another, as the STARC guide asks (2.1.5.1):
    one level only. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       assign y = a ? b : c ? d : e;

    **Fix**

    .. code-block:: systemverilog

       always_comb begin
           if (a) begin
               y = b;
           end else if (c) begin
               y = d;
           end else begin
               y = e;
           end
       end
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        setReported = set()
        for oNode in oFile.nodes("ConditionalExpression"):
            for oBranch in (oNode.left, oNode.right):
                for oInner in [oBranch, *descendants(oBranch)] if oBranch is not None else []:
                    if oInner.kind.name == "ConditionalExpression" and id(oInner) not in setReported:
                        setReported.add(id(oInner))
                        oToken = oFile.token_at(oInner.question)
                        if oToken is not None:
                            yield Problem(oToken, "Do not nest the conditional operator")
