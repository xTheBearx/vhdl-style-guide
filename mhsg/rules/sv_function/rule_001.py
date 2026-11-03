# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import add_automatic, missing_lifetime
from mhsg.rules.sv_tree import TreeRule


class rule_001(TreeRule, structure.Rule):
    """
    This rule checks that functions outside classes are declared automatic or static, as Verible's
    explicit-function-lifetime rule does; the fix adds automatic.

    **Violation**

    .. code-block:: systemverilog

       function logic parity(input logic [7:0] data);

    **Fix**

    .. code-block:: systemverilog

       function automatic logic parity(input logic [7:0] data);
    """

    def __init__(self):
        super().__init__()
        self.fixable = True
        self.solution = "Declare the function automatic or static"

    def problems(self, oFile):
        yield from missing_lifetime(oFile, "function", self.solution)

    def _fix_violation(self, oViolation):
        add_automatic(oViolation)
