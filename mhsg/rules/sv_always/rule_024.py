# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_always.rule_012 import clock_events
from mhsg.rules.sv_always.rule_015 import first_if
from mhsg.rules.sv_nodes import source
from mhsg.rules.sv_tree import Problem, TreeRule, descendants


class rule_024(TreeRule, structure.Rule):
    """
    This rule checks for function calls in the reset test and reset branch of an always block with an asynchronous
    reset, as the STARC guide asks (2.1.2.1). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       if (!rst_ni) q <= init(1'b0);

    **Fix**

    .. code-block:: systemverilog

       if (!rst_ni) q <= 1'b0;
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
            for oPart in (oIf.predicate, oIf.statement):
                for oCall in [oPart, *descendants(oPart)]:
                    if oCall.kind.name == "InvocationExpression" and oCall.left is not None and oCall.left.kind.name != "SystemName":
                        oToken = oFile.token_at(oCall.getFirstToken())
                        if oToken is not None:
                            yield Problem(oToken, f"Do not call {source(oCall.left)} in the reset of the register")
