# -*- coding: utf-8 -*-

from mhsg.design.rule import Finding, Rule, display_name, module_text


class rule_004(Rule):
    """
    This rule reports signals with more than one driver in the synthesized design.

    .. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check SS6.

    GHDL reports two processes that drive the same signal as an error, see design_001.
    This rule finds the drivers GHDL accepts, such as two instances whose outputs are connected to the same signal.
    Tri-state drivers, which assign :code:`'Z'`, are not reported, in the entity or in instances of other entities, and neither is an inout port with one driver inside the entity.

    **Violation**

    .. code-block:: vhdl

       u_a : entity work.source port map (data => bus_data);
       u_b : entity work.source port map (data => bus_data);
    """

    def __init__(self):
        super().__init__()
        self.solution = "Drive the signal from one place"

    def check_design(self, oContext):
        oGraph = oContext.graph()
        if oGraph is None:
            return []
        lReturn = []
        for sModule in oGraph.modules():
            oModule = oGraph.graph(sModule)
            dSignals = {}
            for iBit, lDrivers in oModule.drivers.items():
                # An inout port is driven from outside too, which is how a bidirectional pin works: count the drivers inside
                lCells = [t[0] for t in lDrivers if t[0] is not None]
                if len(lCells) < 2 or all(oModule.drives_tristate(*t) for t in lDrivers if t[0] is not None):
                    continue
                sName = display_name(oModule.bit_name(iBit) or "a signal")
                dSignals.setdefault(sName, set()).update(lCells)
            for sName, setDrivers in sorted(dSignals.items()):
                lCells = sorted(setDrivers)
                lNames = sorted(display_name(s) if oModule.is_instance(s) else "logic" for s in setDrivers)
                sFile, iLine = self.locate(oContext, sModule, lCells, sName)
                lReturn.append(Finding(sFile, iLine, f"Signal {sName} in {module_text(sModule)} has {len(setDrivers)} drivers: {', '.join(lNames)}"))
        return lReturn
