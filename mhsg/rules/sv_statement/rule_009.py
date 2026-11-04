# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants, elements

CHANGES = (
    "AssignmentExpression",
    "NonblockingAssignmentExpression",
    "PostincrementExpression",
    "PostdecrementExpression",
    "PreincrementExpression",
    "PredecrementExpression",
)


class rule_009(TreeRule, structure.Rule):
    """
    This rule checks that the body of a for loop does not change its loop variable, as the STARC guide asks
    (2.9.1.2). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       for (int i = 0; i < 8; i++) begin
           i = i + 1;
       end

    **Fix**

    .. code-block:: systemverilog

       for (int i = 0; i < 8; i += 2) begin
       end
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oLoop in oFile.nodes("ForLoopStatement"):
            setVariables = set()
            for oInitializer in elements(oLoop.initializers):
                oDeclarator = getattr(oInitializer, "declarator", None)
                if oDeclarator is not None:
                    setVariables.add(text(oDeclarator.name))
                elif oInitializer.kind.name == "AssignmentExpression":
                    setVariables.add(text(oInitializer.left.getFirstToken()))
            for oNode in descendants(oLoop.statement) if oLoop.statement is not None else []:
                if oNode.kind.name not in CHANGES:
                    continue
                oTarget = oNode.left if hasattr(oNode, "left") else oNode.operand
                oFirst = oTarget.getFirstToken() if oTarget is not None else None
                if oFirst is not None and text(oFirst) in setVariables:
                    oToken = oFile.token_at(oFirst)
                    if oToken is not None:
                        yield Problem(oToken, f"Do not change the loop variable {text(oFirst)} in the loop")
