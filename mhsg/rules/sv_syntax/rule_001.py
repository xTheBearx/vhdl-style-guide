# -*- coding: utf-8 -*-

import re

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_001(TreeRule, structure.Rule):
    """
    This rule reports code slang cannot parse. The rules on constructs, such as always blocks and labels, skip a file
    with syntax errors, as its syntax tree has constructs missing or misplaced.

    A file is parsed on its own, so macros defined in other files and missing include files are not errors.

    **Violation**

    .. code-block:: systemverilog

       always_comb begin
           y = a +;
       end

    **Fix**

    .. code-block:: systemverilog

       always_comb begin
           y = a + b;
       end
    """

    def __init__(self):
        super().__init__()
        self.checks_syntax_errors = True
        self.solution = "Correct the syntax error"

    def problems(self, oFile):
        for iOffset, sName in oFile.syntax_errors:
            oToken = oFile.token_at_or_after(iOffset)
            if oToken is not None:
                yield Problem(oToken, "Syntax error: " + describe(sName))


def describe(sName):
    """A slang diagnostic name in words, such as ExpectedStatement as expected statement."""
    if sName == "NotAllowedInCU":
        return "not allowed outside a module, interface, program, package or class"
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", sName).lower()
