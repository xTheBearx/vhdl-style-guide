# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_009(TreeRule, structure.Rule):
    """
    This rule checks that an always block is at most **maximum_lines** lines long, 300 by default, as the STARC
    guide asks (2.6.1.4). It is disabled by default; the starc rule set enables it.

    **Violation**

    An always block of 301 lines.

    **Fix**

    Split it into always blocks of related signals.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"
        self.maximum_lines = 300
        self.configuration.append("maximum_lines")

    def problems(self, oFile):
        for oBlock in oFile.nodes("AlwaysBlock", "AlwaysFFBlock", "AlwaysCombBlock", "AlwaysLatchBlock"):
            oFirst, oLast = oBlock.getFirstToken(), oBlock.getLastToken()
            if oFirst is None or oLast is None:
                continue
            iLines = oFile.line_of(oLast.location.offset) - oFile.line_of(oFirst.location.offset) + 1
            if iLines > int(self.maximum_lines):
                oToken = oFile.token_at(oFirst)
                if oToken is not None:
                    yield Problem(oToken, f"Split the always block: it has {iLines} lines, more than {self.maximum_lines}")
