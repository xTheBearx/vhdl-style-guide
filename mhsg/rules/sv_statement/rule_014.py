# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_014(TreeRule, structure.Rule):
    """
    This rule checks that a fork join block is at most **maximum_lines** lines long, 5 by default, as the STARC guide
    recommends (4.1.2.3). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       fork
           send(a);
           send(b);
           send(c);
           receive(d);
       join

    **Fix**

    .. code-block:: systemverilog

       fork
           send_all();
           receive(d);
       join
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"
        self.maximum_lines = 5
        self.configuration.append("maximum_lines")

    def problems(self, oFile):
        for oBlock in oFile.nodes("ParallelBlockStatement"):
            oFirst, oLast = oBlock.getFirstToken(), oBlock.getLastToken()
            iLines = oFile.line_of(oLast.location.offset) - oFile.line_of(oFirst.location.offset) + 1
            if iLines > int(self.maximum_lines):
                oToken = oFile.token_at(oFirst)
                if oToken is not None:
                    yield Problem(oToken, f"Shorten the fork join block: it has {iLines} lines, more than {self.maximum_lines}")
