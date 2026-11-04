# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants

ASSIGNMENTS = ("AssignmentExpression", "NonblockingAssignmentExpression")


class rule_008(TreeRule, structure.Rule):
    """
    This rule checks that an always block assigns at most **maximum_outputs** signals, 15 by default, as the STARC
    guide asks (2.6.1.3; it recommends 5). It is disabled by default; the starc rule set enables it.

    **Violation**

    An always block that assigns 16 signals.

    **Fix**

    Split it into always blocks of related signals.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"
        self.maximum_outputs = 15
        self.configuration.append("maximum_outputs")

    def problems(self, oFile):
        for oBlock in oFile.nodes("AlwaysBlock", "AlwaysFFBlock", "AlwaysCombBlock", "AlwaysLatchBlock"):
            setTargets = set()
            for oNode in descendants(oBlock):
                if oNode.kind.name in ASSIGNMENTS:
                    oFirst = oNode.left.getFirstToken()
                    if oFirst is not None:
                        setTargets.add(text(oFirst))
            if len(setTargets) > int(self.maximum_outputs):
                oToken = oFile.token_at(oBlock.getFirstToken())
                if oToken is not None:
                    sSignals = "1 signal" if len(setTargets) == 1 else f"{len(setTargets)} signals"
                    yield Problem(oToken, f"Split the always block: it assigns {sSignals}, more than {self.maximum_outputs}")
