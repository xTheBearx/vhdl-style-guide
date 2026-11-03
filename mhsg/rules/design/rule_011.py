# -*- coding: utf-8 -*-

from mhsg.design.rule import Finding, Rule


class rule_011(Rule):
    """
    This rule reports signals used both as a clock and as an asynchronous reset.

    .. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check SS9.

    **Violation**

    .. code-block:: vhdl

       process (clk_a, clk_c) is
       begin
         if clk_c = '1' then
           q <= '0';
         elsif rising_edge(clk_a) then
           q <= d;
         end if;
       end process;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Use separate clock and reset signals"

    def check_design(self, oContext):
        oAnalysis = oContext.cdc()
        if oAnalysis is None:
            return []
        lReturn = []
        for oDomain, lCells in oAnalysis.shared:
            sFile, iLine = oAnalysis.locate(lCells[0], oAnalysis.flat.cell_name(lCells[0]).split(".")[-1])
            sCount = f" ({len(lCells)} registers)" if len(lCells) > 1 else ""
            lReturn.append(Finding(sFile, iLine, f"{oDomain.name} is used as a clock and as an asynchronous reset{sCount}"))
        return lReturn
