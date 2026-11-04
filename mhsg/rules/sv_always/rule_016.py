# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_always.rule_012 import clock_events
from mhsg.rules.sv_always.rule_015 import first_if
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants

ASSIGNMENTS = ("NonblockingAssignmentExpression", "AssignmentExpression")


class rule_016(TreeRule, structure.Rule):
    """
    This rule checks that an always block with an asynchronous reset resets every register it assigns, as the STARC
    guide recommends (2.3.6.1): put registers without reset in an always block of their own. It is disabled by
    default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i or negedge rst_ni)
           if (!rst_ni) count <= '0;
           else begin
               count <= count + 1;
               data <= data_i;
           end

    **Fix**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i or negedge rst_ni)
           if (!rst_ni) count <= '0;
           else count <= count + 1;

       always_ff @(posedge clk_i) data <= data_i;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oBlock in oFile.nodes("AlwaysBlock", "AlwaysFFBlock"):
            _, lResets = clock_events(oBlock)
            oIf = first_if(oBlock.statement.statement) if lResets else None
            if oIf is None:
                continue
            setResets = {text(o.expr.getFirstToken()) for o in lResets}
            setReset = {s for s, _ in assigned(oIf.statement)}
            oElse = oIf.elseClause.clause if oIf.elseClause is not None else None
            while oElse is not None and oElse.kind.name == "ConditionalStatement" and tested(oElse) <= setResets:
                setReset.update(s for s, _ in assigned(oElse.statement))
                oElse = oElse.elseClause.clause if oElse.elseClause is not None else None
            setDone = set()
            for sName, oFirst in assigned(oElse) if oElse is not None else []:
                if sName in setReset or sName in setDone:
                    continue
                setDone.add(sName)
                oToken = oFile.token_at(oFirst)
                if oToken is not None:
                    yield Problem(oToken, f"Reset {sName} too, or assign it in an always block without reset")


def assigned(oStatement):
    """(name, first token) of the left side of each assignment under a statement, in order."""
    lReturn = []
    for oNode in [oStatement, *descendants(oStatement)]:
        if oNode.kind.name in ASSIGNMENTS and oNode.left is not None:
            oFirst = oNode.left.getFirstToken()
            lReturn.append((text(oFirst), oFirst))
    return lReturn


def tested(oIf):
    """The names the predicate of an if statement reads."""
    return {text(o.identifier) for o in descendants(oIf.predicate) if o.kind.name in ("IdentifierName", "IdentifierSelectName")}
