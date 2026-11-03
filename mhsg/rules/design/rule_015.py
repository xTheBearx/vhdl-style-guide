# -*- coding: utf-8 -*-

from mhsg.design.rule import Finding, Rule


class rule_015(Rule):
    """
    This rule reports asynchronous resets that are not released synchronously to the clock of the registers they reset.

    .. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check SS15.

    A reset may be asserted asynchronously, but released close to a clock edge it leaves registers in different states.
    Release it through a reset synchronizer in each clock domain: a chain of two or more registers that the reset clears and that load a constant.
    Two cases are reported: a reset input that resets registers directly, and a reset synchronized to one clock that resets registers of another.
    A reset input declared in the domain of the registers under inputs in the cdc section is taken as synchronous.

    **Violation**

    .. code-block:: vhdl

       process (clk, reset) is
       begin
         if reset = '1' then
           q <= '0';
         elsif rising_edge(clk) then
           q <= d;
         end if;
       end process;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Release the reset through a reset synchronizer"

    def check_design(self, oContext):
        oAnalysis = oContext.cdc()
        if oAnalysis is None:
            return []
        lReturn = []
        for oReset in oAnalysis.resets:
            if oReset.kind not in ("raw", "crossing"):
                continue
            oFirst = oReset.cells[0]
            sFile, iLine = oAnalysis.locate(oFirst, oAnalysis.flat.cell_name(oFirst).split(".")[-1])
            sCount = f" ({len(oReset.cells)} registers)" if len(oReset.cells) > 1 else ""
            if oReset.kind == "raw":
                sMessage = f"Reset {oReset.reset} is released asynchronously: it {oReset.detail} without a reset synchronizer{sCount}"
            else:
                sMessage = f"Reset {oReset.reset} is {oReset.detail}{sCount}"
            lReturn.append(Finding(sFile, iLine, sMessage))
        return lReturn
