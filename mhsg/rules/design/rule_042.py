# -*- coding: utf-8 -*-

from mhsg.design import graph
from mhsg.design.rule import Finding, Rule


class rule_042(Rule):
    """
    This rule reports bidirectional top-level ports whose direction is not fixed during the shift of the scan chains.

    .. NOTE:: This is a design rule. It runs in design analysis. It is disabled by default: it needs the inputs that
              select test mode and scan shift, see :code:`test_mode` and :code:`scan_shift` in :doc:`design_analysis`.

    While the scan chains shift, the registers that control the tri-state drivers of the pins take arbitrary values: a
    pin may then drive against the tester. The enable of each tri-state driver of an inout port of the top level must
    be constant when the test_mode and scan_shift inputs of the design section have their values.

    **Violation**

    The output enable of an inout port driven by a register, with no forcing in scan shift.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.disabled_in_design = True
        self.solution = "Force the output enable of the pin during scan shift"

    def check_design(self, oContext):
        oTest = oContext.test_mode(True)
        if oTest is None:
            return []
        oFlat = oTest.flat
        dInout = {}
        for sPort, (sDirection, lNets) in oFlat.top_ports.items():
            if sDirection == "inout":
                for oNet in lNets:
                    dInout[oNet] = sPort
        lReturn = []
        setReported = set()
        for oCell in oFlat.cells:
            if oCell.is_black_box() or not graph.is_tristate({"type": oCell.type, "connections": oCell.connections}):
                continue
            lPorts = sorted({dInout[b] for b in oCell.connections.get("Y", []) if b in dInout})
            if not lPorts:
                continue
            lEnables = oCell.connections.get("EN", oCell.connections.get("E", oCell.connections.get("S", [])))
            if all(oTest.value(b) is not None for b in lEnables):
                continue
            for sPort in lPorts:
                if sPort in setReported:
                    continue
                setReported.add(sPort)
                sFile, iLine = oContext.locate_cell(oCell, sPort)
                lReturn.append(Finding(sFile, iLine, f"During scan shift, the direction of inout port {sPort} is not fixed"))
        return lReturn
