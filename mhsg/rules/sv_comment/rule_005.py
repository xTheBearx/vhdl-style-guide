# -*- coding: utf-8 -*-

from mhsg import parser
from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_005(TreeRule, structure.Rule):
    """
    This rule checks that comments hold only ASCII characters, as the STARC guide recommends (3.5.6.4, 3.5.6.5):
    write comments in English, as some tools cannot read other characters. It is disabled by default; the starc rule
    set enables it.

    **Violation**

    .. code-block:: systemverilog

       // Zähler

    **Fix**

    .. code-block:: systemverilog

       // counter
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oToken in oFile.lAllObjects:
            if isinstance(oToken, parser.comment) and not oToken.get_value().isascii():
                yield Problem(oToken, "Write the comment with ASCII characters only")
