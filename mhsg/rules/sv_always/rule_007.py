# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants


class rule_007(TreeRule, structure.Rule):
    """
    This rule checks for registers clocked on the falling edge of their clock, as the STARC guide recommends
    (1.4.3.6). In an always block with several events, those tested by its first if are asynchronous resets, which
    may use negedge; the others are clocks. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       always_ff @(negedge clk_i) begin
           q <= d;
       end

    **Fix**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i) begin
           q <= d;
       end
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oBlock in oFile.nodes("AlwaysBlock", "AlwaysFFBlock"):
            oStatement = oBlock.statement
            if oStatement is None or oStatement.kind.name != "TimingControlStatement":
                continue
            lEvents = [o for o in descendants(oStatement.timingControl) if o.kind.name == "SignalEventExpression" and text(o.edge)]
            setResets = reset_names(oStatement.statement) if len(lEvents) > 1 else set()
            for oEvent in lEvents:
                sSignal = text(oEvent.expr.getFirstToken()) if oEvent.expr is not None else ""
                if sSignal in setResets or text(oEvent.edge) != "negedge":
                    continue
                oToken = oFile.token_at(oEvent.edge)
                if oToken is not None:
                    yield Problem(oToken, "Clock the register on the rising edge")


def reset_names(oStatement):
    """The names the condition of the first if of an always block tests: its asynchronous resets."""
    while oStatement is not None and oStatement.kind.name == "SequentialBlockStatement":
        lItems = [o for o in oStatement.items if hasattr(o, "kind") and o.kind.name.endswith("Statement")]
        oStatement = lItems[0] if lItems else None
    if oStatement is None or oStatement.kind.name != "ConditionalStatement":
        return set()
    return {text(o.identifier) for o in descendants(oStatement.predicate) if o.kind.name in ("IdentifierName", "IdentifierSelectName")}
