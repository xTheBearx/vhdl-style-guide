# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.port.rule_028 import clock_reset_rank
from mhsg.rules.sv_always.rule_012 import clock_events
from mhsg.rules.sv_always.rule_015 import first_if
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants


class rule_021(TreeRule, structure.Rule):
    """
    This rule checks for registers reset synchronously, an edge triggered always block with one clock whose first if
    tests a reset, as the STARC guide recommends (1.3.1.2): reset them asynchronously. Resets are told by the words
    of their names, as for port_028. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i)
           if (!rst_ni) q <= 1'b0;
           else q <= d;

    **Fix**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i or negedge rst_ni)
           if (!rst_ni) q <= 1'b0;
           else q <= d;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oBlock in oFile.nodes("AlwaysBlock", "AlwaysFFBlock"):
            lClocks, lResets = clock_events(oBlock)
            if len(lClocks) != 1 or lResets:
                continue
            oIf = first_if(oBlock.statement.statement)
            for oName in descendants(oIf.predicate) if oIf is not None else []:
                if oName.kind.name in ("IdentifierName", "IdentifierSelectName") and clock_reset_rank(text(oName.identifier)) == 1:
                    oToken = oFile.token_at(oName.identifier)
                    if oToken is not None:
                        yield Problem(oToken, f"Reset with {text(oName.identifier)} asynchronously")
                    break
