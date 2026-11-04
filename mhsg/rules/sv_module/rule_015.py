# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_015(TreeRule, structure.Rule):
    """
    This rule checks that a module that instantiates other modules holds no logic of its own, always blocks or
    continuous assignments, as the STARC guide recommends (1.6.4.1) for the levels of the hierarchy above the basic
    blocks. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       sub u_sub (.a(a), .y(y));
       assign z = y & en;

    **Fix**

    Move the logic into a module of its own and instantiate it.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oModule in oFile.nodes("ModuleDeclaration"):
            if not any(o.kind.name == "HierarchyInstantiation" for o in oModule.members):
                continue
            for oMember in oModule.members:
                if oMember.kind.name in ("AlwaysBlock", "AlwaysFFBlock", "AlwaysCombBlock", "AlwaysLatchBlock", "ContinuousAssign"):
                    oToken = oFile.token_at(oMember.getFirstToken())
                    if oToken is not None:
                        yield Problem(oToken, "Move the logic to a basic block: this module connects instances")
                    break
