# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule


class rule_038(Rule):
    """
    This rule checks for chains of inverters: concurrent assignments that only invert a signal which another such
    assignment drives.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254 rule set (SS1).

    Such a chain implies logic whose purpose is a delay. Synthesis removes it, so the design does not do what the code
    suggests, and the design analysis does not see the chain in the netlist.

    **Violation**

    .. code-block:: vhdl

       delay_1 <= not trigger;
       delay_2 <= not delay_1;

    **Fix**

    .. code-block:: vhdl

       -- Time the trigger with a register, or with a delay element of the device
    """

    def __init__(self):
        super().__init__()
        self.solution = "Remove the chain of inverters"

    def check(self, oModel, oFile):
        lTokens = oFile.lAllObjects
        for oArchitecture in oModel.architectures:
            dLinks = {}
            for oAssignment in oArchitecture.assignments:
                sSource = inverted_signal(lTokens, oAssignment.index)
                if sSource is not None and not oAssignment.indexed:
                    dLinks[oAssignment.base] = (sSource, oAssignment)
            for sTarget, (sSource, oAssignment) in dLinks.items():
                if sSource in dLinks:
                    self.report(oFile, oAssignment.index, f"Signal {sTarget} inverts {sSource}, which inverts {dLinks[sSource][0]}: a chain of inverters")


def inverted_signal(lTokens, iIndex):
    """Returns the name a concurrent assignment only inverts, as in a <= not b, or None."""
    lValue = []
    bValue = False
    for oToken in lTokens[iIndex:]:
        if isinstance(oToken, model.parser.semicolon):
            break
        if model.is_trivia(oToken):
            continue
        if bValue:
            lValue.append((oToken.get_value() or "").lower())
        elif model.kind(oToken)[1] == "assignment":
            bValue = True
    iInversions = 0
    while lValue[:1] == ["not"] or (len(lValue) >= 2 and lValue[0] == "(" and lValue[-1] == ")"):
        if lValue[0] == "not":
            iInversions += 1
            lValue = lValue[1:]
        else:
            lValue = lValue[1:-1]
    if iInversions % 2 == 1 and len(lValue) == 1 and model.reName.fullmatch(lValue[0]) and lValue[0] not in ("'0'", "'1'"):
        return lValue[0]
    return None
