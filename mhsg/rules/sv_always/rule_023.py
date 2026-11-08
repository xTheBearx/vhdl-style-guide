# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_always.rule_012 import clock_events
from mhsg.rules.sv_nodes import combinational_blocks, text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants, elements


class rule_023(TreeRule, structure.Rule):
    """
    This rule checks that the asynchronous resets of the always blocks of a module are not made by logic in the
    module, a continuous assignment of an expression or an assignment in a combinational always block, as the STARC
    guide recommends (1.3.2.1): generate resets in a module of their own. It is disabled by default; the starc rule
    set enables it.

    **Violation**

    .. code-block:: systemverilog

       assign rst_n = rst_a_n & rst_b_n;
       always_ff @(posedge clk_i or negedge rst_n) ...

    **Fix**

    Generate the reset in a reset module and bring it in through a port.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        setResets = set()
        for oBlock in oFile.nodes("AlwaysBlock", "AlwaysFFBlock"):
            _, lResets = clock_events(oBlock)
            setResets.update(text(o.expr.getFirstToken()) for o in lResets)
        for oAssign in oFile.nodes("ContinuousAssign"):
            for oAssignment in elements(oAssign.assignments):
                if oAssignment.kind.name != "AssignmentExpression" or oAssignment.right is None:
                    continue
                oFirst = oAssignment.left.getFirstToken()
                if text(oFirst) in setResets and oAssignment.right.kind.name not in ("IdentifierName", "IdentifierSelectName"):
                    oToken = oFile.token_at(oFirst)
                    if oToken is not None:
                        yield Problem(oToken, f"Make the reset {text(oFirst)} in a reset module, not with logic here")
        for oBlock in combinational_blocks(oFile):
            for oAssignment in descendants(oBlock):
                if oAssignment.kind.name in ("AssignmentExpression", "NonblockingAssignmentExpression") and oAssignment.left is not None:
                    oFirst = oAssignment.left.getFirstToken()
                    if text(oFirst) in setResets:
                        oToken = oFile.token_at(oFirst)
                        if oToken is not None:
                            yield Problem(oToken, f"Make the reset {text(oFirst)} in a reset module, not with logic here")
