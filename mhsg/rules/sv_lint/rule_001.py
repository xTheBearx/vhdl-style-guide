# -*- coding: utf-8 -*-

from mhsg.rules.sv_lint.diagnostics import Rule


class rule_001(Rule):
    """
    This rule checks for widths that do not match, such as an assignment that truncates a value, as slang
    reports them (WidthTruncate, WidthExpand, PortWidthTruncate and PortWidthExpand).

    .. NOTE:: This is a lint rule. It runs in lint mode and reports what slang finds when it elaborates the file.

    **Violation**

    .. code-block:: systemverilog

       logic [3:0] y;
       assign y = a_i;  // a_i is 8 bits

    **Fix**

    .. code-block:: systemverilog

       logic [3:0] y;
       assign y = a_i[3:0];
    """

    def __init__(self):
        super().__init__()
        self.solution = "Make the widths match"

    def accepts(self, sName):
        return sName.startswith(("Width", "PortWidth"))
