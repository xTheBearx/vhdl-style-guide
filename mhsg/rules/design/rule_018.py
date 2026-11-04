# -*- coding: utf-8 -*-

from mhsg.design.rule import Finding, Rule


class rule_018(Rule):
    """
    This rule reports reset domain crossings: data from a register with one asynchronous reset, directly or through
    logic, into a register of the same clock that another asynchronous reset clears.

    .. NOTE:: This is a design rule. It runs in design analysis.

    Asserting the reset of the source changes its output at any time, so a destination that is not reset with it can
    capture the change metastable. The crossing is safe when the destination is reset whenever the source is: when its
    reset comes from the same reset, or combines it with others, directly or through reset synchronizers.
    Registers without an asynchronous reset are not reported, as their data during a reset is not used, and neither
    are the registers of reset synchronizers.

    **Violation**

    .. code-block:: vhdl

       process (clk, rst_a) is
       begin
         if rst_a = '1' then
           a_r <= '0';
         elsif rising_edge(clk) then
           a_r <= d;
         end if;
       end process;

       process (clk, rst_b) is
       begin
         if rst_b = '1' then
           b_r <= '0';
         elsif rising_edge(clk) then
           b_r <= a_r;
         end if;
       end process;

    **Fix**

    Reset b_r with rst_a too, for example with a reset that combines both, or keep a_r stable while rst_a is asserted.
    """

    def __init__(self):
        super().__init__()
        self.solution = "Reset the destination whenever the source is reset"

    def check_design(self, oContext):
        oAnalysis = oContext.cdc()
        if oAnalysis is None:
            return []
        lReturn = []
        for lCells, sReset, sSourceReset, oSource in oAnalysis.reset_crossings:
            oFirst = lCells[0]
            sFile, iLine = oAnalysis.locate(oFirst, oAnalysis.flat.cell_name(oFirst).split(".")[-1])
            if len(lCells) > 1:
                sDestination = f"{oAnalysis.flat.cell_name(oFirst)} and {len(lCells) - 1} more, reset by {sReset}, capture"
                sThem = "them"
            else:
                sDestination = f"{oAnalysis.flat.cell_name(oFirst)}, reset by {sReset}, captures"
                sThem = "it"
            sMessage = (
                f"{sDestination} {oAnalysis.flat.cell_name(oSource)}, reset by {sSourceReset}: asserting {sSourceReset} alone can make {sThem} metastable"
            )
            lReturn.append(Finding(sFile, iLine, sMessage))
        return lReturn
