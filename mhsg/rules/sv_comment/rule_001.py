# -*- coding: utf-8 -*-

import re

from mhsg import parser
from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_001(TreeRule, structure.Rule):
    """
    This rule checks for synthesis directives and scripts in comments, such as synopsys full_case, parallel_case
    or dc_script_begin, as the STARC guide asks (2.8.1.5, 2.8.5.1, 3.1.2.7). **pattern** is the regular
    expression searched for in comments. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       case (state_q) // synopsys full_case parallel_case

    **Fix**

    .. code-block:: systemverilog

       unique case (state_q)
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"
        self.pattern = "(synopsys|synthesis|ambit|pragma)\\s+(full_case|parallel_case|dc_script_begin)"
        self.configuration.append("pattern")

    def problems(self, oFile):
        for oToken in oFile.lAllObjects:
            if isinstance(oToken, parser.comment) and re.search(self.pattern, oToken.get_value()):
                yield Problem(oToken, "Remove the synthesis directive from the comment")
