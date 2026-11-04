# -*- coding: utf-8 -*-

import re

from mhsg import parser
from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_003(TreeRule, structure.Rule):
    """
    This rule checks that a file starts with a header comment giving each of **header_fields**, regular expressions
    matched ignoring case, by default the module or circuit name, its function, the author and the date, as the STARC
    guide recommends (3.5.3.1). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       module fifo (input logic clk_i);

    **Fix**

    .. code-block:: systemverilog

       // Module:   fifo
       // Function: first in, first out buffer
       // Author:   A. Designer
       // Date:     2026-11-04
       module fifo (input logic clk_i);
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"
        self.header_fields = ["module|circuit", "function|description|purpose", "author", "date|created"]
        self.configuration.append("header_fields")

    def problems(self, oFile):
        lComments = []
        for oToken in oFile.lAllObjects:
            if isinstance(oToken, parser.comment):
                lComments.append(oToken)
            elif not isinstance(oToken, (parser.whitespace, parser.carriage_return, parser.blank_line)):
                break
        if not oFile.lAllObjects:
            return
        if not lComments:
            yield Problem(oFile.lAllObjects[0], "Start the file with a header comment")
            return
        sHeader = "\n".join(o.get_value() for o in lComments)
        lMissing = [s for s in self.header_fields if re.search(s, sHeader, re.IGNORECASE) is None]
        if lMissing:
            yield Problem(lComments[0], f"Give {', '.join(lMissing)} in the file header")
