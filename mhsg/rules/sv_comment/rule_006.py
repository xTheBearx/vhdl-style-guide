# -*- coding: utf-8 -*-

import re

from mhsg import parser
from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_006(TreeRule, structure.Rule):
    """
    This rule checks that the header comment at the start of a file records its changes, matching each of
    **history_fields**, regular expressions matched ignoring case, by default a word such as modified, history or
    revision, as the STARC guide recommends (3.5.3.2) for code that is reused. sv_comment_003 checks the other fields
    of the header. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       // Module: fifo, Author: A. Designer, Date: 2026-11-04

    **Fix**

    .. code-block:: systemverilog

       // Module: fifo, Author: A. Designer, Date: 2026-11-04
       // History: 2026-11-05 B. Reviewer, deeper buffer
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"
        self.history_fields = ["modif|change|history|revision"]
        self.configuration.append("history_fields")

    def problems(self, oFile):
        lComments = []
        for oToken in oFile.lAllObjects:
            if isinstance(oToken, parser.comment):
                lComments.append(oToken)
            elif not isinstance(oToken, (parser.whitespace, parser.carriage_return, parser.blank_line)):
                break
        if not lComments:
            return
        sHeader = "\\n".join(o.get_value() for o in lComments)
        lMissing = [s for s in self.history_fields if re.search(s, sHeader, re.IGNORECASE) is None]
        if lMissing:
            yield Problem(lComments[0], f"Record the changes in the file header: {', '.join(lMissing)}")
