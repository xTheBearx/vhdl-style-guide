# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants


class rule_020(TreeRule, structure.Rule):
    """
    This rule checks that a for loop of an always block with an asynchronous reset does not hold the reset test, an
    if on one of the signals of its event control, as the STARC guide recommends (2.9.2.4): use one loop in the reset
    branch and another in the other branch. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       for (int i = 0; i < 4; i++)
           if (!rst_ni) q[i] <= 1'b0;
           else q[i] <= d[i];

    **Fix**

    .. code-block:: systemverilog

       if (!rst_ni) for (int i = 0; i < 4; i++) q[i] <= 1'b0;
       else for (int i = 0; i < 4; i++) q[i] <= d[i];
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
            setResets = {text(o.expr.getFirstToken()) for o in lEvents} if len(lEvents) > 1 else set()
            if not setResets:
                continue
            for oLoop in [oStatement.statement, *descendants(oStatement.statement)]:
                if oLoop.kind.name != "ForLoopStatement":
                    continue
                for oIf in [oLoop.statement, *descendants(oLoop.statement)]:
                    if oIf.kind.name == "ConditionalStatement" and any(
                        o.kind.name in ("IdentifierName", "IdentifierSelectName") and text(o.identifier) in setResets for o in descendants(oIf.predicate)
                    ):
                        oToken = oFile.token_at(oLoop.forKeyword)
                        if oToken is not None:
                            yield Problem(oToken, "Use one for loop in the reset branch and another in the other branch")
                        break
