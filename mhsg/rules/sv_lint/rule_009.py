# -*- coding: utf-8 -*-

from mhsg.rules.sv_lint import diagnostics
from mhsg.rules.sv_lint.diagnostics import Rule
from mhsg.rules.sv_lint.rule_001 import rule_001
from mhsg.rules.sv_lint.rule_002 import rule_002
from mhsg.rules.sv_lint.rule_003 import rule_003
from mhsg.rules.sv_lint.rule_004 import rule_004
from mhsg.rules.sv_lint.rule_005 import rule_005
from mhsg.rules.sv_lint.rule_006 import rule_006
from mhsg.rules.sv_lint.rule_007 import rule_007
from mhsg.rules.sv_lint.rule_010 import rule_010
from mhsg.rules.sv_lint.rule_017 import rule_017
from mhsg.rules.sv_lint.rule_018 import rule_018

# Warnings that style rules report: a case statement without default is sv_case_001, an unnamed generate block
# sv_generate_001
COVERED = ("CaseDefault", "UnnamedGenerate")


class rule_009(Rule):
    """
    This rule reports the other warnings slang finds when it elaborates the file, such as an index out of range or
    arithmetic between operands of different types, with slang's name of the warning.

    .. NOTE:: This is a lint rule. It runs in lint mode and reports what slang finds when it elaborates the file.

    **Violation**

    .. code-block:: systemverilog

       assign last = data[8];  // data is [7:0]

    **Fix**

    .. code-block:: systemverilog

       assign last = data[7];
    """

    def __init__(self):
        super().__init__()
        self.solution = "Correct the code slang warns about"
        self.lOthers = [o() for o in (rule_001, rule_002, rule_003, rule_004, rule_005, rule_006, rule_007, rule_010, rule_017, rule_018)]

    def accepts(self, sName):
        # Verilator's warnings are sv_lint_011's, and the warnings of mhsg about parameters and macros those of sv_lint_014 to sv_lint_016
        if sName in (diagnostics.PARTIAL_OVERRIDE, diagnostics.REUSED_PARAMETER, diagnostics.GLOBAL_MACRO):
            return False
        return sName not in COVERED and not sName.startswith("verilator.") and not any(o.accepts(sName) for o in self.lOthers)

    def message(self, oDiagnostic):
        return super().message(oDiagnostic) + f" (slang {oDiagnostic.name})"
