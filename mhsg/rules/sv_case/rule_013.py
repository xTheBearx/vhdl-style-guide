# -*- coding: utf-8 -*-

import os

from mhsg.rule_group import structure
from mhsg.rules.sv_flow import reads, targets
from mhsg.rules.sv_nodes import ancestors, source, text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants, elements

ASSIGNMENTS = ("AssignmentExpression", "NonblockingAssignmentExpression")
PROCEDURES = ("AlwaysBlock", "AlwaysFFBlock", "AlwaysCombBlock", "AlwaysLatchBlock", "InitialBlock", "FunctionDeclaration", "TaskDeclaration")


class rule_013(TreeRule, structure.Rule):
    """
    This rule checks that every state of a state machine can be entered and left. It is disabled by default; the
    do254 rule set enables it (CP6).

    A state machine is a case statement on a variable of an enum type, whose items assign the variable or another
    variable of its type, such as the next state. The type is declared in the file or, in lint mode, in another file
    of the run, such as a package; a state can be written with its package, as pkg::Idle. A state that no assignment of the module gives
    those variables, other than the first value of the type, can never be entered, other than by reset; a state
    whose case item assigns no other state can never be left. Both are usually mistakes, and a state that cannot be
    left hangs the machine. A default assignment of a state before the case statement leaves every state. Design
    analysis proves the same through the logic, see design_047 and design_048.

    **Violation**

    .. code-block:: systemverilog

       typedef enum logic [1:0] {Idle, Run, Done, Error} state_e;
       ...
       case (state_q)
           Idle:    if (start) state_d = Run;
           Run:     if (last) state_d = Done;
           Done:    ;                  // never left
           default: state_d = Idle;    // Error is never entered
       endcase

    **Fix**

    .. code-block:: systemverilog

       case (state_q)
           Idle:    if (start) state_d = Run;
           Run:     if (last) state_d = Done; else if (fault) state_d = Error;
           Done:    state_d = Idle;
           default: state_d = Idle;
       endcase
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "Make every state reachable and leavable"

    def problems(self, oFile):
        dTypes = {text(o.name): enum_values(o.type) for o in oFile.nodes("TypedefDeclaration") if o.type is not None and o.type.kind.name == "EnumType"}
        dRun = run_enum_types(oFile)
        for oModule in oFile.nodes("ModuleDeclaration"):
            dVariables = state_variables(oModule, dTypes, dRun)
            if not dVariables:
                continue
            lAssignments = assignments(oModule)
            for oCase in [o for o in descendants(oModule) if o.kind.name == "CaseStatement"]:
                sState = selector_name(oCase)
                if sState not in dVariables:
                    continue
                sType, lValues = dVariables[sState]
                setStates = {s for s, t in dVariables.items() if t[0] == sType}
                lItems = [o for o in elements(oCase.items) if o.kind.name == "StandardCaseItem"]
                if not any(assigns_state(oItem.clause, setStates) for oItem in elements(oCase.items)):
                    # A case statement whose items assign no state is a decoder, not a state machine
                    continue
                setEntered = set()
                for oTarget, oRight in lAssignments:
                    if oTarget in setStates:
                        setEntered.update(value_reads(oRight))
                setEntered.update(returned_values(oModule, sType))
                oToken = oFile.token_at(oCase.getFirstToken())
                for sValue in lValues[1:]:
                    if sValue not in setEntered and oToken is not None:
                        yield Problem(oToken, f"State {sValue} of {sState} is never assigned, so the machine never enters it")
                if default_before(oCase, setStates, lValues):
                    continue
                for oItem in lItems:
                    lChoices = [s for s in (unqualified(source(o)) for o in elements(oItem.expressions)) if s in lValues]
                    if not lChoices or leaves(oItem.clause, setStates, lValues, lChoices):
                        continue
                    oItemToken = oFile.token_at(oItem.getFirstToken())
                    if oItemToken is not None:
                        yield Problem(oItemToken, f"State {lChoices[0]} of {sState} assigns no other state, so the machine never leaves it")


def enum_values(oEnum):
    return [text(o.name) for o in elements(oEnum.members)]


def run_enum_types(oFile):
    """The enum types of the files of the run, when lint mode compiled the run, see svFile/project.py."""
    dProject = getattr(getattr(oFile, "configuration", None), "sv_lint_project", None) or {}
    dEntry = dProject.get(os.path.abspath(oFile.filename)) if getattr(oFile, "filename", None) else None
    if dEntry is None and dProject:
        dEntry = next(iter(dProject.values()))
    return (dEntry or {}).get("enums") or {"qualified": {}, "bare": {}}


def named_type(oType, dTypes, dRun):
    """(type, values) of a named type: an enum type of the file, else of the run, by its bare or qualified name."""
    oName = oType.name
    if oName.kind.name == "IdentifierName":
        sName = text(oName.identifier)
        if sName in dTypes:
            return sName, dTypes[sName]
        if sName in dRun["bare"]:
            return dRun["bare"][sName]
    elif oName.kind.name == "ScopedName":
        sName = "".join(source(oName).split())
        if sName in dRun["qualified"]:
            return sName, dRun["qualified"][sName]
    return None


def state_variables(oModule, dTypes, dRun):
    """The variables of a module of an enum type of the file or the run: name -> (type, values)."""
    dReturn = {}
    for oDeclaration in [o for o in descendants(oModule) if o.kind.name == "DataDeclaration"]:
        oType = oDeclaration.type
        if oType is None:
            continue
        if oType.kind.name == "NamedType":
            tType = named_type(oType, dTypes, dRun)
            if tType is None:
                continue
        elif oType.kind.name == "EnumType":
            tType = (f"@{oType.getFirstToken().location.offset}", enum_values(oType))
        else:
            continue
        for oDeclarator in elements(oDeclaration.declarators):
            dReturn[text(oDeclarator.name)] = tType
    return dReturn


def unqualified(sName):
    """A name without its package or class: Idle for pkg::Idle."""
    return sName.split("::")[-1].strip()


def value_reads(oExpression):
    """The names an expression reads, with the names written with their package, such as pkg::Idle, unqualified."""
    setReturn = {text(o.identifier) for o in reads(oExpression)}
    if oExpression is not None:
        setReturn.update(unqualified(source(o)) for o in [oExpression, *descendants(oExpression)] if o.kind.name == "ScopedName")
    return setReturn


def selector_name(oCase):
    oExpression = oCase.expr
    while oExpression is not None and oExpression.kind.name == "ParenthesizedExpression":
        oExpression = oExpression.expression
    if oExpression is not None and oExpression.kind.name == "IdentifierName":
        return text(oExpression.identifier)
    return None


def assignments(oNode):
    """(target name, right side) of the procedural and continuous assignments under a node."""
    lReturn = []
    for oChild in [oNode, *descendants(oNode)]:
        if oChild.kind.name in ASSIGNMENTS and oChild.left is not None:
            lReturn.extend((o.name, oChild.right) for o in targets(oChild.left))
    return lReturn


def assigns_state(oStatement, setStates):
    return oStatement is not None and hasattr(oStatement, "kind") and any(s in setStates for s, _ in assignments(oStatement))


def returned_values(oModule, sType):
    """The names the functions returning the type return, such as the result of a next state function."""
    setReturn = set()
    for oFunction in [o for o in descendants(oModule) if o.kind.name == "FunctionDeclaration"]:
        oReturnType = oFunction.prototype.returnType
        if oReturnType is not None and oReturnType.kind.name == "NamedType" and type_names(oReturnType) & {sType, unqualified(sType)}:
            for oReturn in [o for o in descendants(oFunction) if o.kind.name == "ReturnStatement"]:
                setReturn.update(value_reads(oReturn.returnValue))
    return setReturn


def type_names(oNamedType):
    """The names of a named type as written: state_e, or pkg::state_e and state_e."""
    sName = "".join(source(oNamedType).split())
    return {sName, unqualified(sName)}


def default_before(oCase, setStates, lValues):
    """True if the procedure of the case statement assigns a state value to a state variable before it."""
    oProcedure = next((o for o in ancestors(oCase) if o.kind.name in PROCEDURES), None)
    if oProcedure is None:
        return False
    iCase = oCase.getFirstToken().location.offset
    for oChild in descendants(oProcedure):
        if oChild.kind.name in ASSIGNMENTS and oChild.left is not None and oChild.getFirstToken().location.offset < iCase:
            if any(o.name in setStates for o in targets(oChild.left)) and value_reads(oChild.right) & set(lValues):
                return True
    return False


def leaves(oStatement, setStates, lValues, lChoices):
    """
    True if a case item may assign another state: a state value other than its own, or anything the rule cannot
    tell, such as the result of a function.
    """
    for sTarget, oRight in assignments(oStatement):
        if sTarget not in setStates:
            continue
        setRead = value_reads(oRight)
        if setRead & (set(lValues) - set(lChoices)):
            return True
        if any(o.kind.name == "InvocationExpression" for o in [oRight, *descendants(oRight)]):
            return True
        if setRead - set(lValues) - setStates:
            return True
    return False
