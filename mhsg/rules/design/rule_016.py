# -*- coding: utf-8 -*-

from mhsg.design.rule import Finding, Rule


class rule_016(Rule):
    """
    This rule reports signals synchronized separately from one clock domain that meet again in logic.

    .. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check CDC1.

    Each synchronizer takes one or two cycles of the destination clock, and which one is random.
    Two signals that change together in the source domain can therefore arrive in different cycles, and logic that
    combines them can see a state the source never had, for example a request without its qualifier.
    Synchronize one signal and derive the others from it in the destination domain, use a handshake, or gray code a counter.
    The bits of one bus count as one signal: a gray-coded bus is meant to be combined, and design_009 reports other buses.

    **Violation**

    .. code-block:: vhdl

       process (clk_b) is
       begin
         if rising_edge(clk_b) then
           start_meta <= start_a;
           start_b    <= start_meta;
           mode_meta  <= mode_a;
           mode_b     <= mode_meta;
           go_b       <= start_b and mode_b;  -- start_a and mode_a meet again
         end if;
       end process;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Synchronize one signal, or use a handshake"

    def check_design(self, oContext):
        oAnalysis = oContext.cdc()
        if oAnalysis is None:
            return []
        lReturn = []
        for lCells, lSignals in oAnalysis.reconvergences:
            oFirst = lCells[0]
            sName = oAnalysis.flat.cell_name(oFirst)
            sFile, iLine = oAnalysis.locate(oFirst, sName.split(".")[-1])
            sSignals = ", ".join(s for s, _ in lSignals)
            sSource = lSignals[0][1].name if lSignals[0][1] != "async" else "async inputs"
            sMore = f" and {len(lCells) - 1} more registers" if len(lCells) > 1 else ""
            sDomain = oAnalysis.cell_clock[id(oFirst)].name
            lReturn.append(Finding(sFile, iLine, f"{sSignals} from {sSource} are synchronized separately and meet again in {sName}{sMore} ({sDomain})"))
        return lReturn
