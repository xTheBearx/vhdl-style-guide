# -*- coding: utf-8 -*-
"""The items of lists that the alignment rules align."""

from mhsg.rules.sv_tree import elements

# Lists of items whose declarations and statements are aligned
BODIES = {
    "ModuleDeclaration": "members",
    "InterfaceDeclaration": "members",
    "ProgramDeclaration": "members",
    "PackageDeclaration": "members",
    "GenerateBlock": "members",
    "SequentialBlockStatement": "items",
    "FunctionDeclaration": "items",
    "TaskDeclaration": "items",
    "ClassDeclaration": "items",
}


def row(oItem, oTarget):
    """A row of an alignment group, or None when the item has nothing to align."""
    return (oItem, oTarget) if oTarget is not None else None


def declared_name(oItem):
    """The name of a declaration of one variable or net, such as logic [7:0] data;, or None."""
    if oItem.kind.name not in ("DataDeclaration", "NetDeclaration", "StructUnionMember"):
        return None
    lDeclarators = elements(oItem.declarators)
    return lDeclarators[0].name if len(lDeclarators) == 1 else None


def assignment_operator(oItem):
    """The operator of a continuous assignment or an assignment statement of one assignment, or None."""
    if oItem.kind.name == "ContinuousAssign":
        lAssignments = elements(oItem.assignments)
        if len(lAssignments) == 1 and lAssignments[0].kind.name == "AssignmentExpression":
            return lAssignments[0].operatorToken
        return None
    if oItem.kind.name == "ExpressionStatement" and oItem.expr.kind.name in ("AssignmentExpression", "NonblockingAssignmentExpression"):
        return oItem.expr.operatorToken
    return None


def parameter_equals(oItem):
    """The = of a parameter or localparam declaration of one parameter with a value, or None."""
    if oItem.kind.name == "ParameterDeclarationStatement":
        oItem = oItem.parameter
    if oItem is None or oItem.kind.name != "ParameterDeclaration":
        return None
    lDeclarators = elements(oItem.declarators)
    if len(lDeclarators) != 1 or lDeclarators[0].initializer is None:
        return None
    return lDeclarators[0].initializer.equals
