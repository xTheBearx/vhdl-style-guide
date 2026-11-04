# -*- coding: utf-8 -*-

from mhsg import parser
from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_002(TreeRule, structure.Rule):
    """
    This rule checks that comments are line comments, starting with :code:`//`, not block comments between :code:`/*`
    and :code:`*/`, as the STARC guide asks (3.5.6.7). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       /* The width of the data */
       localparam int Width = 8;

    **Fix**

    .. code-block:: systemverilog

       // The width of the data
       localparam int Width = 8;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oToken in oFile.lAllObjects:
            if isinstance(oToken, parser.comment) and oToken.get_value().startswith("/*"):
                yield Problem(oToken, "Use // comments")
