# -*- coding: utf-8 -*-

from mhsg.design.rule import Finding, Rule, display_name, module_text


class rule_005(Rule):
    """
    This rule reports registers that never change in the synthesized design.

    .. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check SS18.

    A register is reported when every bit can only ever hold one value: it is assigned only a constant equal to its reset value,
    or only keeps its value.
    Such a register cannot be controlled, so the logic it feeds cannot be tested, and synthesis removes it.
    Registers that are constant only for the generics of this run are reported too: check each configuration that matters.

    **Violation**

    .. code-block:: vhdl

       process (clk, rst) is
       begin
         if rst = '1' then
           busy <= '0';
         elsif rising_edge(clk) then
           busy <= '0';
         end if;
       end process;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Remove the register or make it controllable"

    def check_design(self, oContext):
        oGraph = oContext.graph()
        if oGraph is None:
            return []
        lReturn = []
        lSeen = []
        for sModule in oGraph.modules():
            oModule = oGraph.graph(sModule)
            for sCell in oModule.registers():
                lQ = oModule.cells[sCell].get("connections", {}).get("Q", [])
                lValues = [oModule.register_value(sCell, i) for i in range(len(lQ))]
                if not lValues or any(s is None for s in lValues):
                    continue
                sName = display_name(oModule.bit_name(lQ[0]) if isinstance(lQ[0], int) else None) or "a register"
                # The last assignment is the one in the clocked branch, after the reset
                sFile, iLine = self.locate(oContext, sModule, [sCell], sName, bLast=True)
                if "" in lValues:
                    sValue = "keeps its initial value"
                else:
                    sValue = "is always " + "".join(reversed(lValues))
                tKey = (sFile, iLine, sName, module_text(sModule))
                if tKey in lSeen:
                    continue
                lSeen.append(tKey)
                lReturn.append(Finding(sFile, iLine, f"Register {sName} in {module_text(sModule)} never changes: it {sValue}"))
        return lReturn
