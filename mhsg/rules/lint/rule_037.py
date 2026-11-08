# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule
from mhsg.rules.lint.rule_017 import declared_type, run_enumerated_types, state_signal


class rule_037(Rule):
    """
    This rule checks that every state of a state machine can be entered and left.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254 rule set (CP6).

    A state machine is a case statement on a signal of an enumerated type declared in the file or, in lint mode, in
    another file of the run, such as a package. A state that no
    assignment of the file gives the state signal, or its next state, can never be entered, other than by reset; a
    state whose branch of the case statement assigns no other state can never be left. Both are usually mistakes,
    and a state that cannot be left hangs the machine.

    **Violation**

    .. code-block:: vhdl

       type state_t is (IDLE, RUN, DONE, ERROR);
       ...
       case state is
         when IDLE => if start = '1' then state <= RUN; end if;
         when RUN  => if last = '1' then state <= DONE; end if;
         when DONE => null;                    -- never left
         when others => state <= IDLE;         -- ERROR is never entered
       end case;

    **Fix**

    .. code-block:: vhdl

       case state is
         when IDLE  => if start = '1' then state <= RUN; end if;
         when RUN   => if last = '1' then state <= DONE; elsif fault = '1' then state <= ERROR; end if;
         when DONE  => state <= IDLE;
         when ERROR => state <= IDLE;
       end case;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Make every state reachable and leavable"

    def check(self, oModel, oFile):
        oDeclarations = oFile.get_declarations()
        lTokens = oFile.lAllObjects
        lAssigned = []
        lMachines = []
        for oArchitecture in oModel.architectures:
            lStatements = list(oArchitecture.assignments)
            for oProcess in oArchitecture.processes:
                lStatements.extend(model.assignments(oProcess.statements, "signal"))
                lStatements.extend(model.assignments(oProcess.statements, "variable"))
                for oCase in [o for o in model.walk(oProcess.statements) if isinstance(o, model.Case)]:
                    sState = state_signal(oCase, oDeclarations, lTokens, oFile)
                    if sState is not None:
                        lMachines.append((sState, oCase, oProcess))
            lAssigned.extend(lStatements)
        # States can also be assigned in procedures, such as those declared in a process
        lAssigned.extend(subprogram_assignments(oModel, lTokens))
        for sState, oCase, oProcess in lMachines:
            lFound = [o for o in oDeclarations.find(sState, oCase.index) if o.kind in ("signal", "variable")]
            sType = declared_type(lTokens, lFound[0].index)
            # The values of a type declared in the file, else of one another file of the run declares, such as a package
            lSpelled = enumeration_values(lTokens, oDeclarations, sType) or (
                [] if declares_type(oDeclarations, sType) else run_enumerated_types(oFile).get(sType, [])
            )
            if not lSpelled:
                continue
            dSpelling = {s.lower(): s for s in lSpelled}
            lValues = list(dSpelling)
            # The state signal and the signals of its type, such as the next state, take the values
            setStateSignals = {sState} | {o.base for o in lAssigned if o.base in same_type_names(oDeclarations, lTokens, lFound[0].index)}
            # A case statement on an enumerated signal whose branches assign no state is a decoder, not a state machine
            if not any(o.base in setStateSignals for a in oCase.alternatives for o in model.walk(a.statements) if isinstance(o, model.Assignment)):
                continue
            setEntered = set()
            for oAssignment in lAssigned:
                if oAssignment.base in setStateSignals:
                    setEntered.update(s for s in oAssignment.value_reads if s in lValues)
            for sValue in lValues:
                if sValue not in setEntered and sValue != lValues[0]:
                    self.report(oFile, oCase.index, f"State {dSpelling[sValue]} of {sState} is never assigned, so the machine never enters it")
            # A default assignment of a state before the case statement leaves every state that assigns no other
            lBefore = [o for o in model.walk(oProcess.statements) if isinstance(o, model.Assignment) and o.index < oCase.index]
            if any(o.base in setStateSignals and set(o.value_reads) & set(lValues) for o in lBefore):
                continue
            for oAlternative in oCase.alternatives:
                if oAlternative.others:
                    continue
                lChoices = [s.lower() for s in oAlternative.choice_texts if s.lower() in lValues]
                lTargets = [o for o in model.walk(oAlternative.statements) if isinstance(o, model.Assignment) and o.base in setStateSignals]
                if lChoices and not any(set(o.value_reads) - set(lChoices) for o in lTargets):
                    self.report(oFile, oAlternative.index, f"State {dSpelling[lChoices[0]]} of {sState} assigns no other state, so the machine never leaves it")


def same_type_names(oDeclarations, lTokens, iIndex):
    """The lower case names of the signals and variables declared with the type of the object declared at iIndex."""
    sType = declared_type(lTokens, iIndex)
    return {o.lower_name for o in oDeclarations.declarations if o.kind in ("signal", "variable") and declared_type(lTokens, o.index) == sType}


def declares_type(oDeclarations, sType):
    return any(o.kind == "type" and o.lower_name == sType for o in oDeclarations.declarations)


def enumeration_values(lTokens, oDeclarations, sType):
    """Returns the values of the enumerated type declared in the file, as written and in order, or []."""
    for oDeclaration in oDeclarations.declarations:
        if oDeclaration.kind != "type" or oDeclaration.lower_name != sType:
            continue
        lValues = []
        for oToken in lTokens[oDeclaration.index :]:
            if model.kind(oToken) == ("enumeration_type_definition", "enumeration_literal"):
                lValues.append(oToken.get_value())
            if isinstance(oToken, model.parser.semicolon):
                break
        return lValues
    return []


def subprogram_assignments(oModel, lTokens):
    """Returns the signal and variable assignments in the bodies of the subprograms of the file."""
    lReturn = []
    for iIndex, oToken in enumerate(lTokens):
        if model.kind(oToken) == ("subprogram_body", "begin_keyword"):
            lStatements, _ = oModel._sequence(iIndex + 1, {("subprogram_body", "end_keyword")})  # pylint: disable=protected-access
            lReturn.extend(model.assignments(lStatements, "signal") + model.assignments(lStatements, "variable"))
    return lReturn
