# -*- coding: utf-8 -*-

from mhsg.design.rule import Finding, Rule


class rule_010(Rule):
    """
    This rule reports clocks used as data.

    .. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check SS8.

    A clock from an input port or a black box, such as a PLL, should only reach clock pins.
    Using it in logic or sampling it with a register makes the design depend on the timing of the clock network.
    Logic that gates a clock is reported by design_012 instead.

    **Violation**

    .. code-block:: vhdl

       process (clk_a) is
       begin
         if rising_edge(clk_a) then
           sample <= clk_b;
         end if;
       end process;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Use the clock only on clock pins"

    def check_design(self, oContext):
        oAnalysis = oContext.cdc()
        if oAnalysis is None:
            return []
        dFindings = {}
        for oDomain, oCell in oAnalysis.clock_as_data:
            sFile, iLine = oAnalysis.locate(oCell, oDomain.name)
            dFindings[(sFile, iLine, oDomain.name)] = dFindings.get((sFile, iLine, oDomain.name), 0) + 1
        lReturn = []
        for (sFile, iLine, sClock), iCount in dFindings.items():
            sCount = f" ({iCount} places)" if iCount > 1 else ""
            lReturn.append(Finding(sFile, iLine, f"Clock {sClock} is used as data{sCount}"))
        return lReturn
