# -*- coding: utf-8 -*-

from mhsg.rules.sv_lint.diagnostics import Rule


class rule_005(Rule):
    """
    This rule checks for declarations that are never used: ports, variables, nets, parameters and imports, and
    variables assigned but never read. A file that uses modules, packages or macros of other files is not
    checked, as a signal read there would look unused.

    .. NOTE:: This is a lint rule. It runs in lint mode and reports what slang finds when it elaborates the file.

    **Violation**

    .. code-block:: systemverilog

       logic spare;
       assign spare = a_i;

    **Fix**

    .. code-block:: systemverilog

       // removed
    """

    def __init__(self):
        super().__init__()
        self.solution = "Remove the declaration or use it"

    def accepts(self, sName):
        return sName.startswith("Unused")
