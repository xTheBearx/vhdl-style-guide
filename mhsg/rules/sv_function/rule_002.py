# -*- coding: utf-8 -*-

from mhsg import language
from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import add_automatic, missing_lifetime
from mhsg.rules.sv_tree import TreeRule


class rule_002(TreeRule, structure.Rule):
    """
    This rule checks that tasks outside classes are declared automatic or static, as Verible's
    explicit-task-lifetime rule does; the fix adds automatic.

    **Violation**

    .. code-block:: systemverilog

       task wait_cycles(input int n);

    **Fix**

    .. code-block:: systemverilog

       task automatic wait_cycles(input int n);
    """

    def __init__(self):
        super().__init__()
        # SystemVerilog only: Verilog-2005 cannot declare a task static, and one without automatic is static, so its
        # lifetime is never unclear
        self.languages = (language.SYSTEMVERILOG,)
        self.fixable = True
        self.solution = "Declare the task automatic or static"

    def problems(self, oFile):
        yield from missing_lifetime(oFile, "task", self.solution)

    def _fix_violation(self, oViolation):
        add_automatic(oViolation)
