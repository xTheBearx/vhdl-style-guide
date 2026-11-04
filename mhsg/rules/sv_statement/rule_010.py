# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants


class rule_010(TreeRule, structure.Rule):
    """
    This rule checks that a chain of if and else if in combinational logic ends with an else, as the STARC guide asks
    (2.7.1.3). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       always_comb begin
           if (a) begin
               y = 1'b0;
           end else if (b) begin
               y = 1'b1;
           end
       end

    **Fix**

    .. code-block:: systemverilog

       always_comb begin
           if (a) begin
               y = 1'b0;
           end else begin
               y = 1'b1;
           end
       end
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oBlock in oFile.nodes("AlwaysCombBlock", "AlwaysBlock"):
            if oBlock.kind.name == "AlwaysBlock" and any(o.kind.name == "SignalEventExpression" and text(o.edge) for o in descendants(oBlock)):
                continue
            for oIf in descendants(oBlock):
                if oIf.kind.name != "ConditionalStatement" or (oIf.parent is not None and oIf.parent.kind.name == "ElseClause"):
                    continue
                oLast = oIf
                iBranches = 1
                while oLast.elseClause is not None and oLast.elseClause.clause.kind.name == "ConditionalStatement":
                    oLast = oLast.elseClause.clause
                    iBranches += 1
                if iBranches > 1 and oLast.elseClause is None:
                    oToken = oFile.token_at(oLast.getFirstToken())
                    if oToken is not None:
                        yield Problem(oToken, "End the if chain with an else")
