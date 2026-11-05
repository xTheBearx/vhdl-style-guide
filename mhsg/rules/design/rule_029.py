# -*- coding: utf-8 -*-

from mhsg.design import graph
from mhsg.design.rule import Finding, Rule, display_name, module_text


class rule_029(Rule):
    """
    This rule reports bidirectional nets whose tri-state driver and the logic that reads them are in the same module.

    .. NOTE:: This is a design rule. It runs in design analysis.

    Keeping the tri-state driver and the input cell of a bidirectional bus in separate blocks keeps the paths through
    the pad apart for synthesis and timing analysis, and leaves no combinational path from the driver back into the
    block that drives it.

    **Violation**

    .. code-block:: vhdl

       pin      <= data when oe = '1' else 'Z';
       received <= pin and enable;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Read the bidirectional net in another module than the one that drives it"

    def check_design(self, oContext):
        oGraph = oContext.graph()
        if oGraph is None:
            return []
        lReturn = []
        for sModule in oGraph.modules():
            oModule = oGraph.graph(sModule)
            dReported = {}
            for iBit, lDrivers in oModule.drivers.items():
                lTristate = [t[0] for t in lDrivers if t[0] is not None and graph.is_tristate(oModule.cells[t[0]])]
                if not lTristate:
                    continue
                lReaders = [t[0] for t in oModule.readers.get(iBit, []) if t[0] is not None and t[0] not in lTristate]
                lReaders = [s for s in lReaders if not oModule.is_instance(s)]
                if not lReaders:
                    continue
                sName = display_name(oModule.bit_name(iBit) or "a net")
                dReported.setdefault(sName, (lTristate, lReaders))
            for sName, (lTristate, lReaders) in sorted(dReported.items()):
                sFile, iLine = self.locate(oContext, sModule, lReaders, sName)
                lReturn.append(Finding(sFile, iLine, f"Bidirectional net {sName} is driven and read in {module_text(sModule)}"))
        return lReturn
