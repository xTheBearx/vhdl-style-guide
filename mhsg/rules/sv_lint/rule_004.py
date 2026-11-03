# -*- coding: utf-8 -*-

from mhsg.rules.sv_lint.diagnostics import Rule


class rule_004(Rule):
    """
    This rule checks for nets declared implicitly by their use, which hides typing mistakes; the default_nettype
    none directive makes them errors. A file that uses modules, packages or macros of other files is not
    checked, as a name defined there would look like an implicit net.

    .. NOTE:: This is a lint rule. It runs in lint mode and reports what slang finds when it elaborates the file.

    **Violation**

    .. code-block:: systemverilog

       assign valid = data_i[0];  // valid is not declared

    **Fix**

    .. code-block:: systemverilog

       logic valid;
       assign valid = data_i[0];
    """

    def __init__(self):
        super().__init__()
        self.solution = "Declare the net"

    def accepts(self, sName):
        return sName.startswith("ImplicitNet")
