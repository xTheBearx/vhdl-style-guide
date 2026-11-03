# -*- coding: utf-8 -*-

from mhsg.rules.sv_lint.diagnostics import Rule


class rule_006(Rule):
    """
    This rule checks for case items that duplicate or overlap others, which can never be matched.

    .. NOTE:: This is a lint rule. It runs in lint mode and reports what slang finds when it elaborates the file.

    **Violation**

    .. code-block:: systemverilog

       case (s_i)
           4'd1: y = 0;
           4'd1: y = 1;

    **Fix**

    .. code-block:: systemverilog

       case (s_i)
           4'd1: y = 0;
           4'd2: y = 1;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Remove the duplicate case item"

    def accepts(self, sName):
        return sName.startswith(("CaseDup", "CaseOverlap"))
