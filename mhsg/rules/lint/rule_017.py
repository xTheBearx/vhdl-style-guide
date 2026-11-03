# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule


class rule_017(Rule):
    """
    This rule checks that a state machine recovers from illegal states.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254_plus rule set.

    A state machine is a case statement on a signal of an enumerated type declared in the file.
    Its :code:`when others` choice must assign a state, so an illegal state caused by a single event upset leads back to a defined state.
    Synthesis tools remove that recovery logic unless told to keep it, so the :code:`attributes` option can list attributes,
    such as :code:`fsm_safe_state`, of which the state signal must have at least one.

    **Violation**

    .. code-block:: vhdl

       case state is
         when IDLE => state <= START;
         when START => state <= IDLE;
         when others => null;
       end case;

    **Fix**

    .. code-block:: vhdl

       case state is
         when IDLE => state <= START;
         when START => state <= IDLE;
         when others => state <= IDLE;
       end case;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Recover to a defined state"
        self.attributes = []
        self.configuration.append("attributes")

    def check(self, oModel, oFile):
        oDeclarations = oFile.get_declarations()
        setAttributed = attributed_signals(oFile, [s.lower() for s in self.attributes])
        lChecked = []
        for oArchitecture in oModel.architectures:
            for oProcess in oArchitecture.processes:
                for oCase in [o for o in model.walk(oProcess.statements) if isinstance(o, model.Case)]:
                    sState = state_signal(oCase, oDeclarations, oFile.lAllObjects)
                    if sState is None:
                        continue
                    lOthers = [o for o in oCase.alternatives if o.others]
                    lTargets = [o.base for o in model.assignments(lOthers[0].statements)] if lOthers else []
                    if lOthers and not lTargets:
                        self.report(oFile, lOthers[0].index, f"Assign a defined state in the when others choice of the state machine on {sState}")
                    if self.attributes and sState not in setAttributed and sState not in lChecked:
                        lChecked.append(sState)
                        self.report(
                            oFile,
                            oCase.index,
                            f"Give {sState} one of the attributes {', '.join(self.attributes)} so synthesis keeps the recovery logic",
                        )


def state_signal(oCase, oDeclarations, lTokens):
    """Returns the signal a case statement selects on if its type is an enumerated type declared in the file, else None."""
    lNames = model.names(oCase.selector)
    if len(lNames) != 1:
        return None
    sName = lNames[0].split(".")[0]
    lFound = [o for o in oDeclarations.find(sName, oCase.index) if o.kind in ("signal", "variable")]
    if not lFound:
        return None
    return sName if declared_type(lTokens, lFound[0].index) in enumerated_types(oDeclarations, lTokens) else None


def declared_type(lTokens, iIndex):
    """Returns the lower case type mark of the object declared at the token index."""
    for oToken in lTokens[iIndex:]:
        if model.kind(oToken) == ("type_mark", "name"):
            return oToken.get_value().lower()
        if isinstance(oToken, model.parser.semicolon):
            return None
    return None


def enumerated_types(oDeclarations, lTokens):
    """Returns the lower case names of the enumerated types declared in the file."""
    setReturn = set()
    for oDeclaration in oDeclarations.declarations:
        if oDeclaration.kind != "type":
            continue
        for oToken in lTokens[oDeclaration.index :]:
            if model.kind(oToken)[0] == "enumeration_type_definition":
                setReturn.add(oDeclaration.lower_name)
                break
            if isinstance(oToken, model.parser.semicolon):
                break
    return setReturn


def attributed_signals(oFile, lAttributes):
    """Returns the lower case names of the signals with an attribute specification for any of the attributes."""
    setReturn = set()
    sAttribute = None
    bNames = False
    for oToken in oFile.lAllObjects:
        tKind = model.kind(oToken)
        if tKind == ("attribute_specification", "attribute_designator"):
            sAttribute = oToken.get_value().lower()
        elif tKind == ("attribute_specification", "of_keyword"):
            bNames = sAttribute in lAttributes
        elif tKind[0] == "attribute_specification" and tKind[1] in ("is_keyword", "semicolon"):
            bNames = False
        elif bNames and not model.is_trivia(oToken) and model.reName.match(oToken.get_value() or ""):
            setReturn.add(oToken.get_value().lower())
    return setReturn
