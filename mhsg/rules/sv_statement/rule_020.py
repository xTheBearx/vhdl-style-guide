# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_statement.rule_019 import chain, chain_heads, compact
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_020(TreeRule, structure.Rule):
    """
    This rule checks for conditions of an if, else if chain that repeat an earlier condition of the chain, so their
    branch is never taken, as the STARC guide asks (2.7.2.2). It is disabled by default; the starc rule set enables
    it.

    **Violation**

    .. code-block:: systemverilog

       if (a) y = 1'b1;
       else if (a) y = 1'b0;

    **Fix**

    .. code-block:: systemverilog

       if (a) y = 1'b1;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oHead in chain_heads(oFile):
            dSeen = {}
            for oPredicate, _ in chain(oHead):
                if oPredicate is None:
                    continue
                sCondition = compact(oPredicate)
                if sCondition in dSeen:
                    oToken = oFile.token_at(oPredicate.getFirstToken())
                    if oToken is not None:
                        yield Problem(oToken, f"Remove the branch: its condition repeats the one on line {dSeen[sCondition]}")
                else:
                    dSeen[sCondition] = oFile.line_of(oPredicate.getFirstToken().location.offset)
