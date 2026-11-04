# -*- coding: utf-8 -*-

from pyslang.syntax import SyntaxNode  # pylint: disable=import-error

from mhsg import language
from mhsg.lint.rule import Rule
from mhsg.rules.sv_nodes import declared_names, text
from mhsg.rules.sv_tree import descendants, elements

IDENTIFIERS = ("IdentifierName", "IdentifierSelectName")
ASSIGNMENTS = ("AssignmentExpression", "NonblockingAssignmentExpression")


class rule_008(Rule):
    """
    This rule checks that the sensitivity list of a combinational always block names every signal and port of the
    file that the block reads. A missing signal makes simulation differ from synthesis; always_comb or always @*
    avoids the list altogether.

    The signals a function or task of the file reads count as read by the blocks that call it. A hierarchical name,
    such as u_sub.valid, must be listed as written; a member of a signal, such as cfg.mode, needs the signal. A
    variable the block declares, or writes on every path before reading it, needs no entry: a write in both branches
    of an if and else, or in every item of a case with a default, is on every path.

    .. NOTE:: This is a lint rule. It runs in lint mode.

    **Violation**

    .. code-block:: systemverilog

       always @(a_i) begin
           y = a_i & b_i;
       end

    **Fix**

    .. code-block:: systemverilog

       always_comb begin
           y = a_i & b_i;
       end
    """

    def __init__(self):
        super().__init__()
        self.languages = (language.SYSTEMVERILOG,)
        self.solution = "Add the signals to the sensitivity list, or use always_comb"

    def check(self, oModel, oFile):
        if getattr(oFile, "dNodes", None) is None or oFile.syntax_errors:
            return
        setSignals = {text(oName) for sKind, oName in declared_names(oFile) if sKind in ("signal", "port")}
        dSubprograms = subprograms(oFile, setSignals)
        dIndexes = {id(o): i for i, o in enumerate(oFile.lAllObjects)}
        for oBlock in oFile.nodes("AlwaysBlock"):
            oStatement = oBlock.statement
            if oStatement is None or oStatement.kind.name != "TimingControlStatement":
                continue
            oControl = oStatement.timingControl
            if oControl.kind.name != "EventControlWithExpression":
                continue
            lEvents = [o for o in descendants(oControl) if o.kind.name == "SignalEventExpression"]
            if not lEvents or any(text(o.edge) for o in lEvents):
                continue
            setListed = {name_of(o.expr) for o in lEvents} | {compact(o.expr) for o in lEvents}
            setRead = read_names(oStatement.statement, setSignals, dSubprograms)
            lMissing = sorted(n for n in setRead if (n in setSignals or "." in n) and n not in setListed)
            oToken = oFile.token_at(oControl.getFirstToken())
            if lMissing and oToken is not None and id(oToken) in dIndexes:
                self.report(oFile, dIndexes[id(oToken)], "Add " + ", ".join(lMissing) + " to the sensitivity list, or use always_comb")


class Subprogram:
    """A function or task of the file: the module signals it reads, and the directions of its arguments."""

    def __init__(self, oNode):
        self.node = oNode
        oPrototype = oNode.prototype
        self.name = compact(oPrototype.name)
        # (name, direction) in order
        self.arguments = []
        if oPrototype.portList is not None:
            sDirection = "input"
            for oPort in elements(oPrototype.portList.ports):
                sWord = text(oPort.direction) if getattr(oPort, "direction", None) is not None else ""
                sDirection = sWord or sDirection
                self.arguments.append((text(oPort.declarator.name), sDirection))
        setLocal = {text(o.name) for o in descendants(oNode) if o.kind.name == "Declarator"}
        setLocal |= {s for s, _ in self.arguments} | {self.name}
        self.local = setLocal
        self.reads = None


def subprograms(oFile, setSignals):
    """{name: Subprogram} of the functions and tasks of a file, with what each reads, following the calls in it."""
    dReturn = {}
    for sKind in ("FunctionDeclaration", "TaskDeclaration"):
        for oNode in oFile.nodes(sKind):
            oSubprogram = Subprogram(oNode)
            dReturn[oSubprogram.name] = oSubprogram
    # What each reads without following calls, then the calls until nothing changes
    dDirect = {}
    dCalls = {}
    for sName, oSubprogram in dReturn.items():
        setRead = set()
        for oItem in oSubprogram.node.items:
            setRead |= read_names(oItem, setSignals, {})
        dDirect[sName] = {s for s in setRead if s not in oSubprogram.local}
        dCalls[sName] = {compact(o.left) for o in descendants(oSubprogram.node) if o.kind.name == "InvocationExpression"} & set(dReturn)
    for sName in dReturn:
        dReturn[sName].reads = set(dDirect[sName])
    bChanged = True
    while bChanged:
        bChanged = False
        for sName, oSubprogram in dReturn.items():
            for sCallee in dCalls[sName]:
                setNew = dReturn[sCallee].reads - oSubprogram.reads
                if setNew:
                    oSubprogram.reads |= setNew
                    bChanged = True
    return dReturn


def unwrap(oNode):
    """The expression of an argument, which pyslang wraps in property and sequence expressions."""
    while oNode is not None and oNode.kind.name in ("SimplePropertyExpr", "SimpleSequenceExpr"):
        oNode = oNode.expr
    return oNode


def compact(oNode):
    """The text of a node without spaces."""
    return "".join(str(oNode).split()) if oNode is not None else ""


def name_of(oExpression):
    oFirst = oExpression.getFirstToken() if oExpression is not None else None
    return text(oFirst)


def read_names(oStatement, setSignals=frozenset(), dSubprograms=None):
    """
    The names a statement reads. A read after the block has written the variable on every path, by assignment or as
    the output argument of a task call, does not count: the block computes the value itself, as it does for the
    variables declared in it. A write in both branches of an if and else, or in every item of a case with a default,
    is on every path. A call of a function or task of the file adds the signals it reads. A hierarchical name, such as
    u_sub.valid, is read as a whole; a member of a signal, such as cfg.mode, reads the signal; a package item, such as
    pkg::WIDTH, is not a signal.
    """
    if oStatement is None:
        return set()
    dSubprograms = dSubprograms or {}
    setLocal = {text(o.name) for o in descendants(oStatement) if o.kind.name == "Declarator"}
    setReturn, _ = flow(oStatement, frozenset(), setSignals, dSubprograms)
    return setReturn - setLocal


def flow(oStatement, setDefined, setSignals, dSubprograms):
    """(names read before the statement writes them, names written on every path after it) of a statement."""
    if oStatement is None:
        return set(), setDefined
    sKind = oStatement.kind.name
    if sKind == "SequentialBlockStatement":
        setReads = set()
        for oItem in elements(oStatement.items):
            setRead, setDefined = flow(oItem, setDefined, setSignals, dSubprograms)
            setReads |= setRead
        return setReads, setDefined
    if sKind == "ConditionalStatement":
        setReads = set()
        for oCondition in elements(oStatement.predicate.conditions):
            setReads |= item_names(oCondition, setSignals, dSubprograms)[0] - setDefined
        setThen, setThenDefined = flow(oStatement.statement, setDefined, setSignals, dSubprograms)
        if oStatement.elseClause is None:
            return setReads | setThen, setDefined
        setElse, setElseDefined = flow(oStatement.elseClause.clause, setDefined, setSignals, dSubprograms)
        return setReads | setThen | setElse, setThenDefined & setElseDefined
    if sKind == "CaseStatement":
        setReads = item_names(oStatement.expr, setSignals, dSubprograms)[0] - setDefined
        lDefined = []
        bDefault = False
        for oItem in elements(oStatement.items):
            if oItem.kind.name == "StandardCaseItem":
                for oExpression in elements(oItem.expressions):
                    setReads |= item_names(oExpression, setSignals, dSubprograms)[0] - setDefined
            bDefault = bDefault or oItem.kind.name == "DefaultCaseItem"
            setRead, setItemDefined = flow(getattr(oItem, "clause", None), setDefined, setSignals, dSubprograms)
            setReads |= setRead
            lDefined.append(setItemDefined)
        if bDefault and lDefined:
            return setReads, frozenset.intersection(*[frozenset(s) for s in lDefined])
        return setReads, setDefined
    setRead, setWritten = item_names(oStatement, setSignals, dSubprograms)
    if sKind == "ExpressionStatement":
        return setRead - setDefined, frozenset(setDefined | setWritten)
    # Loops and other statements may not run, so what they write is not written on every path
    return setRead - setDefined, setDefined


def item_names(oStatement, setSignals, dSubprograms):
    """(names read, names written) of a statement; the targets of its assignments are not reads."""
    lNodes = [oStatement, *descendants(oStatement)]
    setTargets = set()
    setWritten = set()
    for oNode in lNodes:
        if oNode.kind.name in ASSIGNMENTS and oNode.left.kind.name in IDENTIFIERS:
            setTargets.add(oNode.left.identifier.location.offset)
            setWritten.add(text(oNode.left.identifier))
        elif oNode.kind.name == "InvocationExpression" and compact(oNode.left) in dSubprograms and oNode.arguments is not None:
            lArguments = dSubprograms[compact(oNode.left)].arguments
            for iArgument, oArgument in enumerate(elements(oNode.arguments.parameters)):
                if oArgument.kind.name == "NamedArgument":
                    sDirection = dict(lArguments).get(text(oArgument.name), "input")
                else:
                    sDirection = lArguments[iArgument][1] if iArgument < len(lArguments) else "input"
                oExpression = unwrap(oArgument.expr)
                if sDirection in ("output", "inout", "ref") and oExpression is not None and oExpression.kind.name in IDENTIFIERS:
                    setTargets.add(oExpression.identifier.location.offset)
                    setWritten.add(text(oExpression.identifier))
    setReturn = set()
    lStack = [oStatement]
    while lStack:
        oNode = lStack.pop()
        sKind = oNode.kind.name
        if sKind == "ScopedName":
            if text(oNode.separator) == ".":
                sFirst = name_of(oNode)
                setReturn.add(sFirst if sFirst in setSignals else compact(oNode))
            continue
        if sKind == "InvocationExpression" and compact(oNode.left) in dSubprograms:
            setReturn |= dSubprograms[compact(oNode.left)].reads
            if oNode.arguments is not None:
                lStack.append(oNode.arguments)
            continue
        if sKind in IDENTIFIERS and oNode.identifier.location.offset not in setTargets:
            setReturn.add(text(oNode.identifier))
        lStack.extend(o for o in oNode if isinstance(o, SyntaxNode))
    return setReturn, setWritten
