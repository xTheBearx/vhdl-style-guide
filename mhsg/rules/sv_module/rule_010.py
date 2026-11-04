# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule

LOGIC = ("AlwaysBlock", "AlwaysFFBlock", "AlwaysCombBlock", "ContinuousAssign", "HierarchyInstantiation")


class rule_010(TreeRule, structure.Rule):
    """
    This rule checks that a module with latches, always_latch blocks, holds no other logic, as the STARC guide
    recommends (2.4.1.1, 2.4.1.2): put latches in modules of their own. It is disabled by default; the starc rule set
    enables it.

    **Violation**

    .. code-block:: systemverilog

       always_latch if (en) q <= d;
       assign y = q & a;

    **Fix**

    Move the latch to a module that holds only latches.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oModule in oFile.nodes("ModuleDeclaration"):
            lLatches = [o for o in oModule.members if o.kind.name == "AlwaysLatchBlock"]
            if lLatches and any(o.kind.name in LOGIC for o in oModule.members):
                for oLatch in lLatches:
                    oToken = oFile.token_at(oLatch.keyword)
                    if oToken is not None:
                        yield Problem(oToken, "Put the latch in a module of its own")
