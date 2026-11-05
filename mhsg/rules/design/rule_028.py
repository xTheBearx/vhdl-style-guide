# -*- coding: utf-8 -*-

from mhsg.design import graph
from mhsg.design.rule import Finding, Rule
from mhsg.rules.design.rule_003 import unique


class rule_028(Rule):
    """
    This rule reports tri-state enables that do not come from top inputs only: through logic from a register, a
    latch, a memory or a black box.

    .. NOTE:: This is a design rule. It runs in design analysis. It is disabled by default: it is a rule of design for
              test, for the scan tests of ASICs.

    During a scan test the registers hold test patterns, so an enable that a register drives can turn on two drivers
    of a bus at once. An enable that comes from top inputs, directly or through a decoder of them, is fixed by the
    tester.

    **Violation**

    .. code-block:: vhdl

       bus_data <= data when oe_r = '1' else 'Z';  -- oe_r is a register
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.disabled_in_design = True
        self.solution = "Drive the tri-state enable from top inputs"

    def check_design(self, oContext):
        oFlat = oContext.flat()
        if oFlat is None:
            return []
        lReturn = []
        for oCell in oFlat.cells:
            if not graph.is_tristate(oCell.cell):
                continue
            lEnable = [n for n in oCell.connections.get("S" if "S" in oCell.connections else "EN", []) if graph.is_variable(n)]
            sSource = state_source(oFlat, lEnable)
            if sSource is None:
                continue
            sFile, iLine = oContext.locate_cell(oCell)
            lReturn.append(Finding(sFile, iLine, f"Tri-state enable comes from {sSource}, not from top inputs only"))
        return unique(lReturn)


def state_source(oFlat, lNets):
    """The name of the first register, latch, memory or black box the nets come from through logic, or None."""
    lWork = list(lNets)
    setSeen = set(lWork)
    while lWork:
        oNet = lWork.pop()
        tDriver = oFlat.driver(oNet)
        if tDriver is None or tDriver[0] is None:
            continue
        oCell = tDriver[0]
        if oCell.is_black_box() or graph.is_state(oCell.cell) or oCell.type.startswith("$mem"):
            return oFlat.net_name(oNet)
        for sPort, lInputs in oCell.connections.items():
            if oFlat.direction(oCell, sPort) != "input":
                continue
            for oInput in lInputs:
                if graph.is_variable(oInput) and oInput not in setSeen:
                    setSeen.add(oInput)
                    lWork.append(oInput)
    return None
