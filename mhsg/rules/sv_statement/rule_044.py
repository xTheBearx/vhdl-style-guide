# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import source, text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants, elements


class rule_044(TreeRule, structure.Rule):
    """
    This rule checks for for loops that build priority logic: an if without else in the loop assigns a signal the
    loop variable does not index, so the last iteration whose condition holds wins, as the STARC guide recommends
    against (2.9.1.1). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       for (int i = 0; i < 8; i++)
           if (req[i]) grant = i;

    **Fix**

    Write the priority explicitly, for example with a case statement or a priority encoder function.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oLoop in oFile.nodes("ForLoopStatement"):
            setVariables = loop_variables(oLoop)
            for oIf in [oLoop.statement, *descendants(oLoop.statement)]:
                if oIf.kind.name != "ConditionalStatement" or oIf.elseClause is not None:
                    continue
                for oNode in descendants(oIf.statement):
                    if oNode.kind.name in ("AssignmentExpression", "NonblockingAssignmentExpression") and oNode.left is not None:
                        lNames = {
                            text(o.identifier) for o in [oNode.left, *descendants(oNode.left)] if o.kind.name in ("IdentifierName", "IdentifierSelectName")
                        }
                        if not lNames & setVariables:
                            oToken = oFile.token_at(oNode.left.getFirstToken())
                            if oToken is not None:
                                yield Problem(oToken, f"The loop makes priority logic for {source(oNode.left)}: write it as such")
                            break


def loop_variables(oLoop):
    """The names of the variables a for loop declares or initializes."""
    setReturn = set()
    for oInitializer in elements(oLoop.initializers):
        if oInitializer.kind.name == "ForVariableDeclaration" and oInitializer.declarator is not None:
            setReturn.add(text(oInitializer.declarator.name))
        elif getattr(oInitializer, "left", None) is not None:
            setReturn.add(text(oInitializer.left.getFirstToken()))
    return setReturn
