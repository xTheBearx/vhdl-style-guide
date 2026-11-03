# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule
from mhsg.rules.lint.rule_017 import declared_type, enumerated_types

STATE_WORDS = ("state", "fsm", "st")
SINGLE_BIT_TYPES = ("std_logic", "std_ulogic", "bit", "boolean")


class rule_027(Rule):
    """
    This rule checks that state machines declare their states with an enumerated type.

    .. NOTE:: This is a lint rule. It runs in lint mode and implements DO-254 check CP5.

    A state machine is a case statement on a signal whose name contains the word state, fsm or st.
    Single-bit signals, such as a toggle, are not checked.
    With an enumerated type, tools show state names and the synthesis tool chooses the encoding, which can then be changed without editing the code.
    Projects that require hard-coded encodings should disable this rule.

    **Violation**

    .. code-block:: vhdl

       signal state : std_logic_vector(1 downto 0);

    **Fix**

    .. code-block:: vhdl

       type state_t is (IDLE, START, STOP);
       signal state : state_t;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Use an enumerated state type"

    def check(self, oModel, oFile):
        oDeclarations = oFile.get_declarations()
        setEnumerated = enumerated_types(oDeclarations, oFile.lAllObjects)
        lReported = []
        for oArchitecture in oModel.architectures:
            for oProcess in oArchitecture.processes:
                for oCase in [o for o in model.walk(oProcess.statements) if isinstance(o, model.Case)]:
                    lNames = model.names(oCase.selector)
                    if len(lNames) != 1 or "." in lNames[0] or lNames[0] in lReported:
                        continue
                    sName = lNames[0]
                    if not any(sWord in STATE_WORDS for sWord in sName.split("_")):
                        continue
                    lFound = [o for o in oDeclarations.find(sName, oCase.index) if o.kind in ("signal", "variable")]
                    if not lFound:
                        continue
                    sType = declared_type(oFile.lAllObjects, lFound[0].index)
                    # A single bit, such as a toggle, needs no enumerated type
                    if sType is not None and sType not in setEnumerated and sType not in SINGLE_BIT_TYPES:
                        lReported.append(sName)
                        self.report(oFile, oCase.index, f"Declare the states of {sName} with an enumerated type instead of {sType}")
