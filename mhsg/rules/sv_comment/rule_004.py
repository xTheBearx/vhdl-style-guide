# -*- coding: utf-8 -*-

from mhsg import parser
from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import inside, text
from mhsg.rules.sv_tree import Problem, TreeRule, elements


class rule_004(TreeRule, structure.Rule):
    """
    This rule checks that each port and each signal of a module is declared with a comment, at the end of its line or
    on the line before, as the STARC guide recommends (3.5.6.3). It is disabled by default; the starc rule set
    enables it.

    **Violation**

    .. code-block:: systemverilog

       logic [7:0] count;

    **Fix**

    .. code-block:: systemverilog

       logic [7:0] count;  // words in the buffer
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        setLines = set()
        for iIndex, oToken in enumerate(oFile.lAllObjects):
            if isinstance(oToken, parser.comment):
                setLines.add(oFile.oTokenMap.get_line_number_of_index(iIndex))
        lNames = [o.declarator.name for o in oFile.nodes("ImplicitAnsiPort") if o.declarator is not None]
        for oNode in oFile.nodes("DataDeclaration", "NetDeclaration"):
            if not inside(oNode, "FunctionDeclaration", "TaskDeclaration", "ClassDeclaration") and inside(oNode, "ModuleDeclaration", "InterfaceDeclaration"):
                lNames += [o.name for o in elements(oNode.declarators)]
        for oName in lNames:
            iLine = oFile.line_of(oName.location.offset)
            if iLine not in setLines and iLine - 1 not in setLines:
                oToken = oFile.token_at(oName)
                if oToken is not None:
                    yield Problem(oToken, f"Describe {text(oName)} in a comment")
