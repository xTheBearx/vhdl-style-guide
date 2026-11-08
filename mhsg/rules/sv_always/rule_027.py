# -*- coding: utf-8 -*-

import re

from mhsg.rule_group import structure
from mhsg.rules.port.rule_028 import clock_reset_rank
from mhsg.rules.sv_always.rule_012 import clock_events
from mhsg.rules.sv_always.rule_015 import polarities
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants, elements

ASSIGNMENTS = ("AssignmentExpression", "NonblockingAssignmentExpression")
# The names of active low resets, as for sv_naming_017
ACTIVE_LOW = re.compile(r".*_(n|x|b|l)(i|o|io)?|.*(rst|reset|clr|clear|set)(n|b)(_(i|o|io))?")


class rule_027(TreeRule, structure.Rule):
    """
    This rule checks that every register has a reset: an edge triggered always block without an asynchronous reset
    holds registers without reset, but for those assigned in the reset branch of an if at the top level of the block
    that tests a synchronous reset. Resets are told by the words of their names, as for port_028. Registers written through an index that is a name, such as mem[addr], are
    memories and are not checked; the registers of an always block with a reset are checked by sv_always_016.
    Registers without a reset on purpose, such as the flip-flops of a synchronizer, should be justified. It is disabled
    by default; the do254 rule set enables it (SS14).

    **Violation**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i)
           q <= d;

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
            if not lClocks or lResets:
                continue
            oStatement = oBlock.statement.statement
            lBranches = reset_branches(oStatement)
            setReset = {text(o.left.getFirstToken()) for oBranch in lBranches for o in assignments(oBranch)}
            setDone = set()
            for oNode in assignments(oStatement):
                if is_memory(oNode.left):
                    continue
                oFirst = oNode.left.getFirstToken()
                sName = text(oFirst)
                if sName in setDone or sName in setReset:
                    continue
                setDone.add(sName)
                oToken = oFile.token_at(oFirst)
                if oToken is not None:
                    sReason = "reset it in the reset branch" if lBranches else "give it a reset"
                    yield Problem(oToken, f"The register {sName} has no reset: {sReason}, or justify it without one")


def assignments(oStatement):
    """The assignments under a statement, in order."""
    return [o for o in [oStatement, *descendants(oStatement)] if o.kind.name in ASSIGNMENTS and o.left is not None]


def reset_branches(oStatement):
    """
    The branches of the if statements at the top level of an always block that test a synchronous reset, a signal
    with a reset name, taken while it is active: the then branch of if (!rst_n) or if (rst), the else of if (rst_n).
    """
    lItems = [oStatement]
    if oStatement is not None and oStatement.kind.name == "SequentialBlockStatement":
        lItems = [o for o in oStatement.items if hasattr(o, "kind")]
    lReturn = []
    for oItem in lItems:
        if oItem is None or oItem.kind.name != "ConditionalStatement":
            continue
        dTested = {}
        for oPattern in elements(oItem.predicate.conditions):
            dTested.update(polarities(oPattern.expr))
        lResets = [(s, b) for s, b in dTested.items() if clock_reset_rank(s) == 1]
        if len(lResets) != 1:
            continue
        sName, bHigh = lResets[0]
        # The branch taken while the reset is active: active low names are tested low
        if bHigh != bool(ACTIVE_LOW.fullmatch(sName.lower())):
            lReturn.append(oItem.statement)
        elif oItem.elseClause is not None:
            lReturn.append(oItem.elseClause.clause)
    return lReturn


def is_memory(oTarget):
    """Whether the target of an assignment is written through an index that is a name, such as mem[addr]."""
    for oChild in [oTarget, *descendants(oTarget)]:
        if oChild.kind.name == "ElementSelect":
            if any(o.kind.name in ("IdentifierName", "IdentifierSelectName") for o in descendants(oChild)):
                return True
    return False
