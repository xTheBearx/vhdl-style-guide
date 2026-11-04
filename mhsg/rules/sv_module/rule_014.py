# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.port.rule_028 import clock_reset_rank
from mhsg.rules.sv_always.rule_012 import clock_events
from mhsg.rules.sv_always.rule_015 import first_if
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants


class rule_014(TreeRule, structure.Rule):
    """
    This rule checks that registers with a synchronous reset are in modules of their own, without other registers, as
    the STARC guide recommends (1.3.1.4). Synchronous resets are told as for sv_always_021. It is disabled by
    default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i) if (!srst_n) a <= '0; else a <= d;
       always_ff @(posedge clk_i or negedge rst_n) ...

    **Fix**

    Move the registers with a synchronous reset to a module of their own.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oModule in oFile.nodes("ModuleDeclaration"):
            lSynchronous, bOther = [], False
            for oBlock in [o for o in oModule.members if o.kind.name in ("AlwaysBlock", "AlwaysFFBlock")]:
                lClocks, lResets = clock_events(oBlock)
                if not lClocks:
                    continue
                oIf = first_if(oBlock.statement.statement) if len(lClocks) == 1 and not lResets else None
                if oIf is not None and any(
                    o.kind.name in ("IdentifierName", "IdentifierSelectName") and clock_reset_rank(text(o.identifier)) == 1 for o in descendants(oIf.predicate)
                ):
                    lSynchronous.append(oBlock)
                else:
                    bOther = True
            for oBlock in lSynchronous if bOther else []:
                oToken = oFile.token_at(oBlock.keyword)
                if oToken is not None:
                    yield Problem(oToken, "Put the registers with a synchronous reset in a module of their own")
