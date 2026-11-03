# -*- coding: utf-8 -*-

from mhsg.design.rule import Finding, Rule


class rule_001(Rule):
    """
    This rule reports the errors GHDL finds when it analyzes and elaborates the design.

    .. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 checks CP1 and CP13.

    GHDL reports, among others, wrong types, names that are not declared, and ranges that do not match.
    A generic of the top entity without a default value must be set in the design section, since GHDL would otherwise use the leftmost value of its type.
    Design analysis stops at the first step with errors, so later steps and the other design rules do not run until they are fixed.

    **Violation**

    .. code-block:: vhdl

       signal tx_index : std_logic_vector(14 downto 0);
       tx_index <= rf2fe_vec;  -- rf2fe_vec is of another type
    """

    def __init__(self):
        super().__init__()
        self.solution = "Fix the error"

    def check_design(self, oContext):
        lReturn = []
        lSeen = []
        for oMessage in oContext.result.messages:
            # Both synthesis runs elaborate the design, so the same message can come twice
            tKey = (oMessage.file, oMessage.line, oMessage.text)
            if oMessage.severity in (None, "error") and tKey not in lSeen:
                lSeen.append(tKey)
                sSource = "Design" if oMessage.stage == "configuration" else "GHDL"
                lReturn.append(Finding(oMessage.file, oMessage.line, f"{sSource} {oMessage.stage} error: {oMessage.text}"))
        return lReturn
