# -*- coding: utf-8 -*-

from mhsg.design import netlist
from mhsg.design.rule import Finding, Rule


class rule_002(Rule):
    """
    This rule reports latches in the synthesized design.

    .. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check SS4.

    It finds the latches synthesis infers, including those in other files and those lint_009 cannot see,
    for example from a case statement on an enumerated type that does not assign a signal in every choice.
    The latch is reported at the assignment in the process that infers it.

    **Violation**

    .. code-block:: vhdl

       process (all) is
       begin
         if en = '1' then
           q <= a;
         end if;
       end process;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Assign the signal on every path"

    def check_design(self, oContext):
        if oContext.netlist is None:
            return []
        # Latches in a generate loop, or for each bit of a vector, come from the same assignment: report it once
        dLatches = {}
        for sModule, sCell, dCell in oContext.netlist.latches():
            dConnections = dCell.get("connections", {})
            lBits = dConnections.get("Q") or dConnections.get("Y") or []
            sSignal = oContext.netlist.bit_name(sModule, lBits[0]) if lBits else None
            sFile, iLine = oContext.refine(oContext.netlist.location(sModule, sCell), sSignal)
            tKey = (sFile, iLine, sSignal or "a signal", netlist.module_name(sModule))
            dLatches[tKey] = dLatches.get(tKey, 0) + 1
        lReturn = []
        for (sFile, iLine, sSignal, sModule), iCount in dLatches.items():
            sCount = f" ({iCount} latches)" if iCount > 1 else ""
            lReturn.append(Finding(sFile, iLine, f"Synthesis infers a latch for {sSignal} in {sModule}{sCount}"))
        return lReturn
