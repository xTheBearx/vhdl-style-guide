# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule


class rule_011(Rule):
    """
    This rule checks that a reset signal is used with one polarity and one style throughout a file.

    .. NOTE:: This is a lint rule. It runs in lint mode and implements DO-254 check SS13.

    The reset of a clocked process is the signal tested before the clock edge (asynchronous), or the signal with a reset name tested first after it (synchronous).
    Using the same reset as active high in one place and active low in another, or both asynchronously and synchronously, causes unintended behaviour around reset.

    **Violation**

    .. code-block:: vhdl

       if rising_edge(clk_master) then
         if rst_master = '1' then
           q <= '0';
         end if;
       end if;

       if rst_master = '0' then
         q2 <= '0';
       elsif falling_edge(clk_n) then
         q2 <= d2;
       end if;

    **Fix**

    .. code-block:: vhdl

       if rising_edge(clk_master) then
         if rst_master = '1' then
           q <= '0';
         end if;
       end if;

       if falling_edge(clk_n) then
         if rst_master = '1' then
           q2 <= '0';
         else
           q2 <= d2;
         end if;
       end if;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Use the reset consistently"

    def check(self, oModel, oFile):
        dSeen = {}
        for oArchitecture in oModel.architectures:
            for oProcess in oArchitecture.processes:
                if oProcess.clock is None or oProcess.clock.reset is None or oProcess.clock.reset.name is None:
                    continue
                oReset = oProcess.clock.reset
                # Resets in different conditional generates, such as a generic choice of reset style, may never both exist
                lOthers = [(o, t) for o, t in dSeen.get(oReset.name, []) if model.same_conditional_generates(t, oProcess.generate, oModel.dGenerateConditions)]
                dSeen.setdefault(oReset.name, []).append((oReset, oProcess.generate))
                if not lOthers:
                    continue
                oFirst = lOthers[0][0]
                if None not in (oReset.level, oFirst.level) and oReset.level != oFirst.level:
                    sThis = "high" if oReset.level == "1" else "low"
                    sOther = "high" if oFirst.level == "1" else "low"
                    self.report(oFile, oReset.index, f"Reset {oReset.name} is active {sThis} here but active {sOther} on line {oFirst.line}")
                if oReset.style != oFirst.style:
                    self.report(oFile, oReset.index, f"Reset {oReset.name} is {style(oReset)} here but {style(oFirst)} on line {oFirst.line}")


def style(oReset):
    return "asynchronous" if oReset.style == "async" else "synchronous"
