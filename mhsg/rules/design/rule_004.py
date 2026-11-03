# -*- coding: utf-8 -*-

from mhsg.design.rule import Finding, Rule, display_name, module_text

TRISTATE_TYPES = {"$tribuf", "$_TBUF_"}


class rule_004(Rule):
    """
    This rule reports signals with more than one driver in the synthesized design.

    .. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check SS6.

    GHDL reports two processes that drive the same signal as an error, see design_001.
    This rule finds the drivers GHDL accepts, such as two instances whose outputs are connected to the same signal.
    Tri-state drivers, which assign :code:`'Z'`, are not reported, and neither is an inout port with one driver inside the entity.

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
                if len(lCells) < 2 or all(is_tristate(oModule.cells[s]) for s in lCells):
                    continue
                sName = display_name(oModule.bit_name(iBit) or "a signal")
                dSignals.setdefault(sName, set()).update(lCells)
            for sName, setDrivers in sorted(dSignals.items()):
                lCells = sorted(setDrivers)
                lNames = sorted(display_name(s) if oModule.is_instance(s) else "logic" for s in setDrivers)
                sFile, iLine = self.locate(oContext, sModule, lCells, sName)
                lReturn.append(Finding(sFile, iLine, f"Signal {sName} in {module_text(sModule)} has {len(setDrivers)} drivers: {', '.join(lNames)}"))
        return lReturn


def is_tristate(dCell):
    """Returns whether a cell can release its output: a tri-state buffer, or a multiplexer with a 'z' input, as GHDL builds them."""
    if dCell.get("type") in TRISTATE_TYPES:
        return True
    if dCell.get("type") in ("$mux", "$pmux"):
        dConnections = dCell.get("connections", {})
        return "z" in dConnections.get("A", []) + dConnections.get("B", [])
    return False
