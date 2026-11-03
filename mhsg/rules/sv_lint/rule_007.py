# -*- coding: utf-8 -*-

from mhsg.rules.sv_lint.diagnostics import Rule


class rule_007(Rule):
    """
    This rule checks for comparisons and conversions between signed and unsigned values.

    .. NOTE:: This is a lint rule. It runs in lint mode and reports what slang finds when it elaborates the file.

    **Violation**

    .. code-block:: systemverilog

       if (count == -1) begin  // count is unsigned

    **Fix**

    .. code-block:: systemverilog

       if (count == '1) begin
    """

    def __init__(self):
        super().__init__()
        self.solution = "Convert explicitly between signed and unsigned"

    def accepts(self, sName):
        return sName.startswith("Sign")
