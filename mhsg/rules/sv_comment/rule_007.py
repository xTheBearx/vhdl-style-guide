# -*- coding: utf-8 -*-

from mhsg import parser
from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_007(TreeRule, structure.Rule):
    """
    This rule checks that at least **minimum_comment_percent** percent of the lines of a module, 10 by default, have
    a comment, as the STARC guide recommends (3.5.6.1). Modules of fewer than 10 lines are not checked. It is
    disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       module fifo (...);  // 200 lines, 3 comments

    **Fix**

    Describe the ports, signals and blocks of the module in comments.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"
        self.minimum_comment_percent = 10
        self.configuration.append("minimum_comment_percent")

    def problems(self, oFile):
        setComments = set()
        for iIndex, oToken in enumerate(oFile.lAllObjects):
            if isinstance(oToken, parser.comment):
                setComments.add(oFile.oTokenMap.get_line_number_of_index(iIndex))
        for oModule in oFile.nodes("ModuleDeclaration"):
            iFirst = oFile.line_of(oModule.getFirstToken().location.offset)
            iLast = oFile.line_of(oModule.getLastToken().location.offset)
            iLines = iLast - iFirst + 1
            if iLines < 10:
                continue
            iCommented = sum(1 for i in setComments if iFirst - 1 <= i <= iLast)
            if 100 * iCommented < int(self.minimum_comment_percent) * iLines:
                oToken = oFile.token_at(oModule.header.name)
                if oToken is not None:
                    yield Problem(oToken, f"Comment the module more: {iCommented} of its {iLines} lines have a comment")
