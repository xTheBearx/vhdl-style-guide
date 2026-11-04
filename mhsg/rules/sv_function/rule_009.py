# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import inside, text
from mhsg.rules.sv_tree import Problem, TreeRule, elements


class rule_009(TreeRule, structure.Rule):
    """
    This rule checks that a function ends by assigning its result, with a return statement or an assignment to its
    name, as the STARC guide recommends (2.1.3.4). Functions returning void and methods of classes are not checked.
    It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       function automatic logic parity(input logic [7:0] data);
           parity = ^data;
           $display("parity");
       endfunction

    **Fix**

    .. code-block:: systemverilog

       function automatic logic parity(input logic [7:0] data);
           $display("parity");
           parity = ^data;
       endfunction
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("FunctionDeclaration"):
            oPrototype = oNode.prototype
            if inside(oNode, "ClassDeclaration") or oPrototype.returnType is None or oPrototype.returnType.kind.name == "VoidType":
                continue
            sName = text(oPrototype.name.getLastToken())
            lStatements = [o for o in oNode.items if hasattr(o, "kind") and o.kind.name.endswith("Statement")]
            if lStatements and not result(lStatements[-1], sName):
                oToken = oFile.token_at(oPrototype.name.getFirstToken())
                if oToken is not None:
                    yield Problem(oToken, f"End the function {sName} by assigning its result")


def result(oStatement, sName):
    """
    True if a statement returns a value or assigns the function name: a return, an assignment, a block ending with one,
    or an if with an else or a case with a default whose branches all do.
    """
    sKind = oStatement.kind.name
    if sKind == "ReturnStatement":
        return True
    if sKind == "SequentialBlockStatement":
        lItems = [o for o in oStatement.items if hasattr(o, "kind") and o.kind.name.endswith("Statement")]
        return bool(lItems) and result(lItems[-1], sName)
    if sKind == "ConditionalStatement":
        return oStatement.elseClause is not None and result(oStatement.statement, sName) and result(oStatement.elseClause.clause, sName)
    if sKind == "CaseStatement":
        lItems = list(elements(oStatement.items))
        return any(o.kind.name == "DefaultCaseItem" for o in lItems) and all(result(o.clause, sName) for o in lItems)
    oExpression = getattr(oStatement, "expr", None)
    return sKind == "ExpressionStatement" and oExpression.kind.name == "AssignmentExpression" and text(oExpression.left.getFirstToken()) == sName
