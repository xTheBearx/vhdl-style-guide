# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule


class rule_033(Rule):
    """
    This rule checks for signals of an architecture that are never read.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254 rule set (SS17).

    A signal that is assigned but never read, or neither assigned nor read, is logic without a purpose. Synthesis
    removes it, so the design analysis cannot see it in the netlist. A signal connected to a port of an instance counts
    as read, as the port may be an input.

    **Violation**

    .. code-block:: vhdl

       architecture rtl of filter is
         signal sum   : unsigned(7 downto 0);
         signal spare : std_logic;
       begin
         sum   <= a + b;
         spare <= a(0);
         y     <= sum;
       end architecture rtl;

    **Fix**

    .. code-block:: vhdl

       architecture rtl of filter is
         signal sum : unsigned(7 downto 0);
       begin
         sum <= a + b;
         y   <= sum;
       end architecture rtl;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Remove the signal, or use it"

    def check(self, oModel, oFile):
        lTokens = oFile.lAllObjects
        for oArchitecture in oModel.architectures:
            iEnd = oArchitecture.end if oArchitecture.end is not None else len(lTokens)
            dSignals = {}
            for iIndex in range(oArchitecture.index, iEnd):
                if model.kind(lTokens[iIndex]) == ("signal_declaration", "identifier"):
                    dSignals.setdefault(lTokens[iIndex].get_value().lower(), iIndex)
            if not dSignals:
                continue
            dOccurrences = {}
            for iIndex in range(oArchitecture.index, iEnd):
                oToken = lTokens[iIndex]
                if model.is_trivia(oToken) or iIndex in dSignals.values():
                    continue
                sName = (oToken.get_value() or "").lower().split(".")[0]
                if sName in dSignals:
                    dOccurrences[sName] = dOccurrences.get(sName, 0) + 1
            dTargets = {}
            lAssignments = list(oArchitecture.assignments)
            for oProcess in oArchitecture.processes:
                lAssignments.extend(model.assignments(oProcess.statements))
            for oAssignment in lAssignments:
                dTargets[oAssignment.base] = dTargets.get(oAssignment.base, 0) + 1
            for sName, iIndex in dSignals.items():
                iOccurrences = dOccurrences.get(sName, 0)
                if iOccurrences == 0:
                    self.report(oFile, iIndex, f"Signal {lTokens[iIndex].get_value()} is never assigned or read")
                elif iOccurrences <= dTargets.get(sName, 0):
                    self.report(oFile, iIndex, f"Signal {lTokens[iIndex].get_value()} is assigned but never read")
