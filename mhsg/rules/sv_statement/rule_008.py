# -*- coding: utf-8 -*-

from pyslang.syntax import SyntaxNode  # pylint: disable=import-error

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_008(TreeRule, structure.Rule):
    """
    This rule checks that if statements are nested at most **maximum_depth** deep, 7 by default, as the STARC guide
    asks (2.7.3.1). An else if continues its if, so it does not nest deeper. It is disabled by default; the starc rule
    set enables it.

    **Violation**

    Eight if statements, each inside the branch of the one before.

    **Fix**

    Combine the conditions, or move the inner logic to a function or an always block of its own.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"
        self.maximum_depth = 7
        self.configuration.append("maximum_depth")

    def problems(self, oFile):
        lStack = [
            (o, 0)
            for o in oFile.nodes(
                "AlwaysBlock",
                "AlwaysFFBlock",
                "AlwaysCombBlock",
                "AlwaysLatchBlock",
                "InitialBlock",
                "FunctionDeclaration",
                "TaskDeclaration",
            )
        ]
        setSeen = set()
        while lStack:
            oNode, iDepth = lStack.pop()
            if id(oNode) in setSeen:
                continue
            setSeen.add(id(oNode))
            if oNode.kind.name == "ConditionalStatement":
                if iDepth > int(self.maximum_depth):
                    oToken = oFile.token_at(oNode.getFirstToken())
                    if oToken is not None:
                        yield Problem(oToken, f"Nest if statements at most {self.maximum_depth} deep")
                lStack.append((oNode.statement, iDepth))
                if oNode.elseClause is not None:
                    oClause = oNode.elseClause.clause
                    # An else if continues the if
                    lStack.append((oClause, iDepth - 1 if oClause.kind.name == "ConditionalStatement" else iDepth))
                continue
            for oChild in oNode:
                if isinstance(oChild, SyntaxNode):
                    lStack.append((oChild, iDepth + 1 if oChild.kind.name == "ConditionalStatement" else iDepth))
