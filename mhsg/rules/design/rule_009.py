# -*- coding: utf-8 -*-

from mhsg.design import cdc
from mhsg.design.rule import Finding, Rule


class rule_009(Rule):
    """
    This rule reports clock domain crossings with a synchronizer that can still fail.

    .. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check CDC1.

    Two hazards are reported:

    * logic between the clock domains before the first synchronizer stage, which can glitch and be captured;
    * the bits of a bus synchronized one by one, which can arrive in different clock cycles, unless the bus is gray coded.

    The bits of an input port declared independent in the cdc section of the design, such as
    :code:`d_i: {domain: async, bits: independent}`, are signals of their own and not a bus.

    **Violation**

    .. code-block:: vhdl

       sync_meta <= valid_a and ready_a;  -- logic on signals of clock domain a, captured by clk_b
       sync_b    <= sync_meta;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Register the signal in the source domain before the synchronizer"

    def check_design(self, oContext):
        oAnalysis = oContext.cdc()
        if oAnalysis is None:
            return []
        lReturn = []
        for oCrossing in oAnalysis.crossings:
            if oCrossing.status not in cdc.HAZARDS:
                continue
            sFile, iLine = oAnalysis.locate(oCrossing.cell, oCrossing.name.split(".")[-1])
            if oCrossing.status == cdc.LOGIC:
                sMessage = f"Logic on {oCrossing.source_text()} before synchronizer {oCrossing.name} ({oCrossing.clock.name}) can glitch"
            else:
                sMessage = f"{oCrossing.source_text()} is synchronized bit by bit into {oCrossing.name} ({oCrossing.clock.name}); the bits can arrive in different cycles"
            lReturn.append(Finding(sFile, iLine, sMessage))
        return lReturn
