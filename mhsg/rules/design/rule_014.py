# -*- coding: utf-8 -*-

from mhsg.design.rule import Finding, Rule


class rule_014(Rule):
    """
    This rule reports asynchronous resets made inside the design by logic or by a register that is not a reset synchronizer.

    .. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check SS12.

    Logic on an asynchronous reset can glitch and reset registers when it should not.
    The output of a reset synchronizer, a chain of registers that the reset clears and that load a constant, is not reported.

    **Violation**

    .. code-block:: vhdl

       process (clk, soft_reset, reset) is
       begin
         if (soft_reset or reset) = '1' then
           q <= '0';
         elsif rising_edge(clk) then
           q <= d;
         end if;
       end process;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Use a reset from an input or a reset synchronizer"

    def check_design(self, oContext):
        oAnalysis = oContext.cdc()
        if oAnalysis is None:
            return []
        lReturn = []
        for oReset in oAnalysis.resets:
            if oReset.kind != "generated":
                continue
            oFirst = oReset.cells[0]
            sFile, iLine = oAnalysis.locate(oFirst, oAnalysis.flat.cell_name(oFirst).split(".")[-1])
            sCount = f" ({len(oReset.cells)} registers)" if len(oReset.cells) > 1 else ""
            if oReset.reset.startswith("logic of "):
                sMessage = f"Asynchronous reset is made by {oReset.reset}{sCount}"
            else:
                sMessage = f"Asynchronous reset {oReset.reset} is {oReset.detail}{sCount}"
            lReturn.append(Finding(sFile, iLine, sMessage))
        return lReturn
