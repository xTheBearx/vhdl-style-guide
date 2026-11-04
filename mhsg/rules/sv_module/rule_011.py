# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_statement.rule_017 import high_impedance
from mhsg.rules.sv_tree import Problem, TreeRule, descendants


class rule_011(TreeRule, structure.Rule):
    """
    This rule checks that a module with tri-state buffers, assignments of values with z digits, holds no other logic,
    as the STARC guide recommends (2.5.1.1): put tri-state buffers in modules of their own. It is disabled by
    default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       assign bus = oe ? data : 'z;
       always_ff @(posedge clk_i) data <= d;

    **Fix**

    Move the tri-state buffer to a module that holds only tri-state buffers.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oModule in oFile.nodes("ModuleDeclaration"):
            lTristate = []
            bOther = False
            for oMember in oModule.members:
                if oMember.kind.name == "ContinuousAssign" and any(high_impedance(o) for o in descendants(oMember)):
                    lTristate.append(oMember)
                elif oMember.kind.name in ("AlwaysBlock", "AlwaysFFBlock", "AlwaysCombBlock", "AlwaysLatchBlock", "ContinuousAssign", "HierarchyInstantiation"):
                    bOther = True
            if bOther:
                for oAssign in lTristate:
                    oToken = oFile.token_at(oAssign.getFirstToken())
                    if oToken is not None:
                        yield Problem(oToken, "Put the tri-state buffer in a module of its own")
