# -*- coding: utf-8 -*-
"""
Definite assignment in the procedural code of SystemVerilog, for the rules that check variables read before they are
assigned (sv_always_030, sv_always_031).

The walk follows the statements of a block in order and keeps the names that every path so far has assigned with a
blocking assignment of the whole variable. A name read while not in that set may hold the value of an earlier run
of the block. Both branches of an if statement must assign a name for it to be assigned after the statement, and all
items of a case statement, with a default item or as a unique or priority case. The body of a loop may not run, so
what it assigns does not count after it.

Assignments to an element, a slice or a member of a variable do not assign the whole variable; the rules leave out
the variables written only that way.
"""

from pyslang.syntax import SyntaxNode  # pylint: disable=import-error

from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import descendants, elements

# Blocking assignments that read the variable they assign
COMPOUND = {
    "AddAssignmentExpression",
    "SubtractAssignmentExpression",
    "MultiplyAssignmentExpression",
    "DivideAssignmentExpression",
    "ModAssignmentExpression",
    "AndAssignmentExpression",
    "OrAssignmentExpression",
    "XorAssignmentExpression",
    "LogicalLeftShiftAssignmentExpression",
    "LogicalRightShiftAssignmentExpression",
    "ArithmeticLeftShiftAssignmentExpression",
    "ArithmeticRightShiftAssignmentExpression",
}
STEPS = {"PostincrementExpression", "PostdecrementExpression", "UnaryPreincrementExpression", "UnaryPredecrementExpression"}
LOOPS = {"ForLoopStatement", "LoopStatement", "ForeverStatement", "ForeachLoopStatement", "DoWhileStatement"}
NAMES = ("IdentifierName", "IdentifierSelectName")


class Target:
    """The variable an assignment writes: its name, the node of the name, and whether it writes the whole variable."""

    def __init__(self, sName, oNode, bWhole):
        self.name = sName
        self.node = oNode
        self.whole = bWhole


def targets(oLeft):
    """The variables the left side of an assignment writes: a name, a select of a name, a member or a concatenation."""
    while oLeft is not None and oLeft.kind.name == "ParenthesizedExpression":
        oLeft = oLeft.expression
    if oLeft is None:
        return []
    sKind = oLeft.kind.name
    if sKind == "IdentifierName":
        return [Target(text(oLeft.identifier), oLeft, True)]
    if sKind == "IdentifierSelectName":
        return [Target(text(oLeft.identifier), oLeft, False)]
    if sKind == "ScopedName" and first_name(oLeft) is not None:
        oFirst = first_name(oLeft)
        return [Target(text(oFirst.identifier), oFirst, False)]
    if sKind in ("ElementSelectExpression", "MemberAccessExpression"):
        return [Target(o.name, o.node, False) for o in targets(oLeft.left)]
    if sKind in ("ConcatenationExpression", "AssignmentPatternExpression"):
        return [o for oChild in elements(getattr(oLeft, "expressions", None)) for o in targets(oChild)]
    return []


def first_name(oScoped):
    """The first name of a hierarchical name or member written with dots, such as s in s.valid; None for pkg::name."""
    oNode = oScoped
    while oNode.kind.name == "ScopedName":
        if text(oNode.separator) != ".":
            return None
        oNode = oNode.left
    return oNode if oNode.kind.name in NAMES else None


def reads(oNode):
    """
    The name nodes an expression reads: names and selects of names, and the first name of a name with dots, such as
    s of s.valid, but not the names of called functions, the members after a dot or names in a package or class
    scope.
    """
    if oNode is None:
        return []
    lReturn = []
    lStack = [oNode]
    while lStack:
        oItem = lStack.pop()
        sKind = oItem.kind.name
        if sKind in NAMES:
            lReturn.append(oItem)
        if sKind == "ScopedName":
            # A hierarchical name or a member, such as s.valid, reads its first name; pkg::name reads a package
            oFirst = first_name(oItem)
            if oFirst is not None:
                lReturn.append(oFirst)
            continue
        if sKind == "InvocationExpression":
            lStack.extend(o for o in (oItem.arguments,) if o is not None)
            continue
        if sKind == "MemberAccessExpression":
            lStack.append(oItem.left)
            continue
        lStack.extend(o for o in oItem if isinstance(o, SyntaxNode))
    return lReturn


def index_reads(oLeft):
    """The names the selects of the left side of an assignment read, such as i in v[i] = 1."""
    lReturn = []
    for oNode in descendants(oLeft) if oLeft is not None else []:
        if oNode.kind.name == "ElementSelect":
            lReturn.extend(reads(oNode))
    return lReturn


class Flow:
    """
    Walks a statement and calls fRead(name, node, assigned) for each name read, with the names assigned on every path
    before it, and fAssign(target, statement) for each variable a statement writes.
    """

    def __init__(self, fRead, fAssign=None):
        self.fRead = fRead
        self.fAssign = fAssign or (lambda oTarget, oStatement, bBlocking: None)

    def read(self, oExpression, setAssigned):
        for oName in reads(oExpression):
            self.fRead(text(oName.identifier), oName, setAssigned)

    def walk(self, oStatement, setAssigned):
        """Returns the names assigned on every path after the statement."""
        if oStatement is None:
            return setAssigned
        sKind = oStatement.kind.name
        if sKind == "SequentialBlockStatement" or sKind == "ParallelBlockStatement":
            for oItem in oStatement.items:
                if not isinstance(oItem, SyntaxNode):
                    continue
                if oItem.kind.name == "DataDeclaration":
                    for oDeclarator in elements(oItem.declarators):
                        if oDeclarator.initializer is not None:
                            self.read(oDeclarator.initializer, setAssigned)
                            setAssigned = setAssigned | {text(oDeclarator.name)}
                else:
                    setAssigned = self.walk(oItem, setAssigned)
            return setAssigned
        if sKind == "ExpressionStatement":
            return self.expression(oStatement.expr, oStatement, setAssigned)
        if sKind == "ConditionalStatement":
            for oCondition in elements(oStatement.predicate.conditions):
                self.read(oCondition, setAssigned)
            setThen = self.walk(oStatement.statement, setAssigned)
            if oStatement.elseClause is None:
                return setAssigned
            return setThen & self.walk(oStatement.elseClause.clause, setAssigned)
        if sKind == "CaseStatement":
            self.read(oStatement.expr, setAssigned)
            lBranches = []
            bDefault = text(oStatement.uniqueOrPriority) in ("unique", "unique0", "priority")
            for oItem in elements(oStatement.items):
                if oItem.kind.name == "StandardCaseItem":
                    for oExpression in elements(oItem.expressions):
                        self.read(oExpression, setAssigned)
                else:
                    bDefault = bDefault or oItem.kind.name == "DefaultCaseItem"
                oClause = getattr(oItem, "clause", None)
                if isinstance(oClause, SyntaxNode):
                    lBranches.append(self.walk(oClause, setAssigned))
            if not bDefault or not lBranches:
                return setAssigned
            setAfter = lBranches[0]
            for setBranch in lBranches[1:]:
                setAfter = setAfter & setBranch
            return setAfter
        if sKind in LOOPS:
            return self.loop(oStatement, setAssigned)
        if sKind == "TimingControlStatement":
            return self.walk(oStatement.statement, setAssigned)
        # Other statements, such as assertions and returns, only read
        for oChild in oStatement:
            if isinstance(oChild, SyntaxNode):
                self.read(oChild, setAssigned)
        return setAssigned

    def loop(self, oStatement, setAssigned):
        setInside = setAssigned
        for oChild in oStatement:
            if not isinstance(oChild, SyntaxNode):
                continue
            sKind = oChild.kind.name
            if sKind == "ForVariableDeclaration":
                oDeclarator = oChild.declarator
                self.read(oDeclarator.initializer, setInside)
                setInside = setInside | {text(oDeclarator.name)}
            elif sKind in ("AssignmentExpression",) + tuple(COMPOUND) + tuple(STEPS):
                setInside = self.expression(oChild, oStatement, setInside)
            elif sKind == "ForeachLoopList":
                setInside = setInside | {text(o.identifier) for o in descendants(oChild) if o.kind.name == "IdentifierName"}
            elif oChild is getattr(oStatement, "statement", None):
                setBody = self.walk(oChild, setInside)
                if oStatement.kind.name == "DoWhileStatement":
                    setAssigned = setBody
            else:
                self.read(oChild, setInside)
        return setAssigned

    def expression(self, oExpression, oStatement, setAssigned):
        if oExpression is None:
            return setAssigned
        sKind = oExpression.kind.name
        if sKind == "AssignmentExpression" or sKind == "NonblockingAssignmentExpression":
            self.read(oExpression.right, setAssigned)
            for oName in index_reads(oExpression.left):
                self.fRead(text(oName.identifier), oName, setAssigned)
            bBlocking = sKind == "AssignmentExpression"
            for oTarget in targets(oExpression.left):
                self.fAssign(oTarget, oStatement, bBlocking)
                if bBlocking and oTarget.whole:
                    setAssigned = setAssigned | {oTarget.name}
            return setAssigned
        if sKind in COMPOUND or sKind in STEPS:
            oLeft = oExpression.left if sKind in COMPOUND else oExpression.operand
            if sKind in COMPOUND:
                self.read(oExpression.right, setAssigned)
            for oTarget in targets(oLeft):
                self.fRead(oTarget.name, oTarget.node, setAssigned)
                self.fAssign(oTarget, oStatement, True)
                if oTarget.whole:
                    setAssigned = setAssigned | {oTarget.name}
            return setAssigned
        self.read(oExpression, setAssigned)
        return setAssigned


def first_reads(oStatement, setWatched):
    """
    The first node at which each watched name is read before every path has assigned it, in the order of the code.
    """
    dReturn = {}

    def fRead(sName, oNode, setAssigned):
        if sName in setWatched and sName not in setAssigned and sName not in dReturn:
            dReturn[sName] = oNode

    Flow(fRead).walk(oStatement, frozenset())
    return dReturn


def assigned(oStatement):
    """The targets a statement assigns, with whether each assignment is blocking."""
    lReturn = []
    Flow(lambda sName, oNode, setAssigned: None, lambda oTarget, oAt, bBlocking: lReturn.append((oTarget, bBlocking))).walk(oStatement, frozenset())
    return lReturn


def assigned_by(oExpression):
    """The targets an assignment expression writes, with whether each assignment is blocking."""
    lReturn = []
    Flow(lambda sName, oNode, setAssigned: None, lambda oTarget, oAt, bBlocking: lReturn.append((oTarget, bBlocking))).expression(
        oExpression,
        None,
        frozenset(),
    )
    return lReturn
