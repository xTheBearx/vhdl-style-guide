# -*- coding: utf-8 -*-

from mhsg import parser
from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule

# Lists of statements and declarations, by the node holding them
LISTS = {
    "SequentialBlockStatement": "items",
    "ParallelBlockStatement": "items",
    "FunctionDeclaration": "items",
    "TaskDeclaration": "items",
    "ModuleDeclaration": "members",
    "InterfaceDeclaration": "members",
    "ProgramDeclaration": "members",
    "PackageDeclaration": "members",
    "GenerateBlock": "members",
    "GenerateRegion": "members",
    "ClassDeclaration": "items",
}


class rule_003(TreeRule, structure.Rule):
    """
    This rule checks for more than one statement or declaration on a line, as the STARC guide asks
    (3.1.4.4, at most one assignment per line). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       valid_d = 1'b0; ready_d = 1'b1;

    **Fix**

    .. code-block:: systemverilog

       valid_d = 1'b0;
       ready_d = 1'b1;
    """

    def __init__(self):
        super().__init__()
        self.fixable = True
        self.disable = True
        self.solution = "Move the statement to its own line"

    def problems(self, oFile):
        dLines = {}
        iLine = 1
        for oToken in oFile.lAllObjects:
            if isinstance(oToken, parser.carriage_return):
                iLine += 1
            else:
                dLines[id(oToken)] = iLine
        for sKind, sField in LISTS.items():
            for oNode in oFile.nodes(sKind):
                iPrevious = None
                for oItem in getattr(oNode, sField, None) or []:
                    oFirst = oFile.token_at(oItem.getFirstToken())
                    oLast = oFile.token_at(oItem.getLastToken())
                    if oFirst is None or oLast is None:
                        iPrevious = None
                        continue
                    if iPrevious is not None and dLines.get(id(oFirst)) == iPrevious:
                        yield Problem(oFirst, self.solution)
                    iPrevious = dLines.get(id(oLast))

    def _fix_violation(self, oViolation):
        oViolation.set_tokens([parser.carriage_return(), *oViolation.get_tokens()])
