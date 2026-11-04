# -*- coding: utf-8 -*-

from mhsg.design.rule import Finding, Rule


class rule_016(Rule):
    """
    This rule reports signals synchronized separately from one clock domain that meet again.

    .. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check CDC1.

    Each synchronizer takes one or two cycles of the destination clock, and which one is random.
    Two signals that change together in the source domain can therefore arrive in different cycles, and logic that
    combines them can see a state the source never had, for example a request without its qualifier.
    Two synchronizers of the same signal can disagree for a cycle in the same way.
    Every synchronizer tags its output, and the tags follow the signal through logic, registers and memories of the destination domain.
    A reconvergence is reported where tags of two synchronizers first meet: at a register, a memory, a black box input or an output.
    The inputs a black box declares synchronous to one of its clock pins count as one place, and a declared path through a black box is followed.
    Synchronize one signal and derive the others from it in the destination domain, use a handshake, or gray code a counter.
    The bits of one bus count as one signal: a gray-coded bus is meant to be combined, and design_009 reports other buses.
    A synchronous reset, an input that loads a constant into two or more registers, is a reset path rather than data
    and is not followed, unless :code:`follow_resets` is true; the crossing report lists the meetings through resets either way.

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
        self.follow_resets = False
        self.configuration.append("follow_resets")

    def check_design(self, oContext):
        oAnalysis = oContext.cdc()
        if oAnalysis is None:
            return []
        lReturn = []
        lReconvergences = oAnalysis.reconvergences + (oAnalysis.reset_reconvergences if self.follow_resets else [])
        for lEndpoints, lSignals in lReconvergences:
            oFirst = lEndpoints[0]
            sFile, iLine = oAnalysis.reconvergence_location(oFirst)
            sSignals = " and ".join(f"{t[0]} (by {t[1]})" for t in lSignals)
            sSource = lSignals[0][2].name if lSignals[0][2] != "async" else "async inputs"
            sMore = f" and {len(lEndpoints) - 1} more" if len(lEndpoints) > 1 else ""
            sClock = oAnalysis.endpoint_clock(oFirst)
            sWhere = oAnalysis.endpoint_name(oFirst) + sMore + (f" ({sClock})" if sClock else "")
            lReturn.append(Finding(sFile, iLine, f"Separately synchronized {sSignals} from {sSource} meet again in {sWhere}"))
        return lReturn
