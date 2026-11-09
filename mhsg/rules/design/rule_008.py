# -*- coding: utf-8 -*-

from mhsg.design import cdc
from mhsg.design.rule import Finding, Rule


class rule_008(Rule):
    """
    This rule reports signals that cross from one clock domain to another without a synchronizer.

    .. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check CDC1.

    A register that captures a signal from an asynchronous clock domain can go metastable.
    A single-bit crossing needs a synchronizer: two or more registers in series in the destination domain, the first fed directly from a register of the source domain and feeding only the next.
    Data captured while an enable synchronized to the destination clock holds it, as in a handshake, is safe: the enable comes from the second or a later stage of a synchronizer.
    Clocks are asynchronous unless the design section groups them, see the design analysis documentation, where crossings can also be waived with a justification.
    A waiver without a justification is reported by this rule.

    **Violation**

    .. code-block:: vhdl

       process (clk_b) is
       begin
         if rising_edge(clk_b) then
           flag_b <= flag_a;  -- flag_a is clocked by clk_a
         end if;
       end process;

    **Fix**

    .. code-block:: vhdl

       process (clk_b) is
       begin
         if rising_edge(clk_b) then
           flag_meta <= flag_a;
           flag_b    <= flag_meta;
         end if;
       end process;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Synchronize the signal to the destination clock"

    def check_design(self, oContext):
        oAnalysis = oContext.cdc()
        if oAnalysis is None:
            return []
        lReturn = [Finding(None, 0, f"Waiver for {s} has no justification") for s in oAnalysis.waiver_errors]
        for oCrossing in oAnalysis.crossings:
            if oCrossing.status != cdc.UNSYNCHRONIZED:
                continue
            sFile, iLine = oAnalysis.locate(oCrossing.cell, oCrossing.name.split(".")[-1])
            sHow = "without a synchronizer" if oCrossing.stages < 2 else "through an enable or reset"
            lReturn.append(Finding(sFile, iLine, f"{oCrossing.name} ({oCrossing.clock.name}) captures {oCrossing.source_text()} {sHow}"))
        return lReturn
