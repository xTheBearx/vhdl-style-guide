# -*- coding: utf-8 -*-

from mhsg.design.rule import Finding, Rule, display_name, module_text


class rule_003(Rule):
    """
    This rule reports combinational loops in the synthesized design.

    .. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check SS3.

    A combinational loop feeds the output of logic back to its input without a register in between.
    Unlike lint_008, which checks one process, it finds loops through several processes, concurrent statements and instances of other entities.
    Latches, which design_002 reports, are not reported again.

    **Violation**

    .. code-block:: vhdl

       a <= b and c;
       b <= a or d;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Break the loop with a register"

    def check_design(self, oContext):
        oGraph = oContext.graph()
        if oGraph is None:
            return []
        lReturn = []
        for sModule in oGraph.modules():
            oModule = oGraph.graph(sModule)
            for lLoop in oModule.loops():
                setNames = {s for b in lLoop for s in oGraph.netlist.bit_names(sModule, b) if not s.startswith("$")}
                # Name the signals of the architecture; the ports they drive only if there are none
                lNames = sorted({display_name(s) for s in setNames if s not in oModule.ports} or {display_name(s) for s in setNames})
                lCells = [s for s in (oModule.driving_cell(b) for b in lLoop) if s is not None]
                lInstances = sorted({display_name(s) for s in lCells if oModule.is_instance(s)})
                sFile, iLine = self.locate(oContext, sModule, lCells, lNames[0] if lNames else None)
                sThrough = ", ".join(lNames[:5]) + (", ..." if len(lNames) > 5 else "") if lNames else "unnamed logic"
                sMessage = f"Combinational loop through {sThrough} in {module_text(sModule)}"
                if lInstances:
                    sMessage += " and instance " + ", ".join(lInstances)
                lReturn.append(Finding(sFile, iLine, sMessage))
        return lReturn
