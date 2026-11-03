# -*- coding: utf-8 -*-

from mhsg.design.rule import Finding, Rule


class rule_013(Rule):
    """
    This rule reports clocks made inside the design by a register, such as a clock divider, or by logic.

    .. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check SS11.

    A clock from a register or logic is not on the clock network of the device, so it has more skew, and timing analysis needs it to be declared.
    Use a clock enable in the domain of the original clock, or a clock management block of the device.
    Registers on a divided clock are in the clock domain of the clock that is divided.

    **Violation**

    .. code-block:: vhdl

       div <= not div when rising_edge(clk);

       process (div) is
       begin
         if rising_edge(div) then
           q <= d;
         end if;
       end process;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Use a clock enable"

    def check_design(self, oContext):
        oAnalysis = oContext.cdc()
        if oAnalysis is None:
            return []
        lReturn = []
        for oDomain in sorted(oAnalysis.clocks.values(), key=lambda o: o.name):
            if oDomain.registers == 0 or not (oDomain.kind == "register" or (oDomain.kind == "logic" and not oDomain.parent)):
                continue
            sFile, iLine = oAnalysis.locate(oDomain.cell, oDomain.name.split(".")[-1])
            sBy = "a register" if oDomain.kind == "register" else "logic"
            sFrom = f" from {oDomain.parent.name}" if oDomain.parent else ""
            lReturn.append(Finding(sFile, iLine, f"Clock {oDomain.name} is made by {sBy}{sFrom} ({registers(oDomain.registers)})"))
        return lReturn


def registers(iCount):
    return f"{iCount} register" if iCount == 1 else f"{iCount} registers"
