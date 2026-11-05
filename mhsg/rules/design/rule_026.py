# -*- coding: utf-8 -*-

import functools

from mhsg.design import graph
from mhsg.design.rule import Finding, Rule, display_name, module_text
from mhsg.rules.design.rule_003 import unique


def _predecessors(oModule, dLatchInputs, iBit):
    return oModule.comb_drivers(iBit) + dLatchInputs.get(iBit, [])


class rule_026(Rule):
    """
    This rule reports loops through latches: logic that feeds a latch its own output, through other logic and latches.

    .. NOTE:: This is a design rule. It runs in design analysis.

    A latch is transparent while it is enabled, so a loop through it behaves as a combinational loop for as long as
    the enable is active, see design_003, which reports the loops without a latch. A latch that holds its own value,
    its enable off, is not a loop.

    **Violation**

    .. code-block:: vhdl

       process (en, b) is
       begin
         if en = '1' then
           a <= not b;
         end if;
       end process;

       b <= a;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Break the loop with a flip-flop"

    def check_design(self, oContext):
        oGraph = oContext.graph()
        if oGraph is None:
            return []
        lReturn = []
        for sModule in oGraph.modules():
            oModule = oGraph.graph(sModule)
            if not oModule.latch_cells:
                continue
            dLatchInputs = {}
            for sLatch in oModule.latch_cells:
                lOutputs = [b for _, _, b in oModule.output_bits(sLatch)]
                lInputs = [b for b in oModule.input_bits(sLatch) if b not in lOutputs]
                for iBit in lOutputs:
                    dLatchInputs.setdefault(iBit, []).extend(lInputs)

            predecessors = functools.partial(_predecessors, oModule, dLatchInputs)

            for lComponent in graph.strongly_connected(sorted(oModule.all_bits()), predecessors):
                setComponent = set(lComponent)
                if not setComponent & set(dLatchInputs):
                    continue
                if len(lComponent) == 1 and lComponent[0] not in predecessors(lComponent[0]):
                    continue
                lLatches = sorted({oModule.driving_cell(b) for b in lComponent if b in dLatchInputs} - {None})
                setNames = {s for b in lComponent for s in oGraph.netlist.bit_names(sModule, b) if not s.startswith("$")}
                lNames = sorted({display_name(s) for s in setNames if s not in oModule.ports} or {display_name(s) for s in setNames})
                sThrough = ", ".join(lNames[:5]) + (", ..." if len(lNames) > 5 else "") if lNames else "unnamed logic"
                sFile, iLine = self.locate(oContext, sModule, lLatches, lNames[0] if lNames else None)
                lReturn.append(Finding(sFile, iLine, f"Loop through latches: {sThrough} in {module_text(sModule)}"))
        return unique(lReturn)
