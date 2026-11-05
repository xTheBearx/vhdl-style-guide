# -*- coding: utf-8 -*-

from mhsg.design import graph
from mhsg.design.rule import Finding, Rule
from mhsg.rules.design.rule_003 import unique


class rule_027(Rule):
    """
    This rule reports chains of more than **maximum_stages** latches, 2 by default, enabled by the same signal with
    the same polarity: on the same clock phase.

    .. NOTE:: This is a design rule. It runs in design analysis.

    Latches open on the same phase let data race through every stage of the chain while the enable is active, so the
    timing of the chain is that of the logic through all of them. The chain is followed through logic, not through
    flip-flops or latches of another phase.

    **Violation**

    Three latches in a row, each enabled while clk is high.
    """

    def __init__(self):
        super().__init__()
        self.solution = "Alternate the phases of the latches, or use flip-flops"
        self.maximum_stages = 2
        self.configuration.append("maximum_stages")

    def check_design(self, oContext):
        oFlat = oContext.flat()
        if oFlat is None or oContext.netlist is None:
            return []
        setLatches = {(s, c) for s, c, _ in oContext.netlist.latches()}
        dLatches = {id(o): o for o in oFlat.cells if (o.module, o.name) in setLatches}
        if not dLatches:
            return []
        dPhase = {iId: phase(oFlat, o) for iId, o in dLatches.items()}
        # The latches of the same phase that feed each latch through logic
        dFeeders = {}
        for iId, oLatch in dLatches.items():
            dFeeders[iId] = [i for i in feeding_latches(oFlat, oLatch, dLatches) if dPhase[i] is not None and dPhase[i] == dPhase[iId]]
        dDepth = {}

        def depth(iId, setPath=()):
            if iId in dDepth:
                return dDepth[iId]
            if iId in setPath:
                # A loop, which design_026 reports
                return 1
            iDepth = 1 + max((depth(i, setPath + (iId,)) for i in dFeeders[iId]), default=0)
            dDepth[iId] = iDepth
            return iDepth

        lReturn = []
        for iId, oLatch in dLatches.items():
            iStages = depth(iId)
            # Report the last latch of each chain that is too long: one no other latch of the chain reads
            if iStages <= int(self.maximum_stages) or any(iId in dFeeders[j] and depth(j) > iStages for j in dLatches):
                continue
            sName = oFlat.cell_name(oLatch, "Q" if "Q" in oLatch.connections else "Y")
            sFile, iLine = oContext.locate_cell(oLatch, sName.split(".")[-1])
            lReturn.append(Finding(sFile, iLine, f"Latch {sName} ends a chain of {iStages} latches on the same phase, more than {self.maximum_stages}"))
        return unique(lReturn)


def phase(oFlat, oCell):
    """(enable net, polarity) of a latch: a $dlatch cell, or a multiplexer that feeds its output back."""
    if oCell.type.startswith("$dlatch") or oCell.type.startswith("$_DLATCH"):
        lEnable = oCell.connections.get("EN", [])
        return (lEnable[0], oCell.parameter("EN_POLARITY", 1)) if lEnable else None
    lSelect = oCell.connections.get("S", [])
    if not lSelect:
        return None
    # The multiplexer holds its output on the branch that reads it back: it is open on the other value
    lOutputs = set(oCell.connections.get("Y", []))
    bHoldsOnA = bool(lOutputs & set(oCell.connections.get("A", [])))
    return (lSelect[0], 1 if bHoldsOnA else 0)


def data_nets(oCell):
    if "D" in oCell.connections:
        return list(oCell.connections["D"])
    lOutputs = set(oCell.connections.get("Y", []))
    return [b for s in ("A", "B") for b in oCell.connections.get(s, []) if b not in lOutputs]


def feeding_latches(oFlat, oLatch, dLatches):
    """The ids of the latches whose outputs reach the data input of a latch through logic."""
    lWork = [n for n in data_nets(oLatch) if graph.is_variable(n)]
    setSeen = set(lWork)
    lReturn = []
    while lWork:
        oNet = lWork.pop()
        tDriver = oFlat.driver(oNet)
        if tDriver is None or tDriver[0] is None:
            continue
        oCell = tDriver[0]
        if id(oCell) in dLatches:
            if oCell is not oLatch:
                lReturn.append(id(oCell))
            continue
        if oCell.is_black_box() or graph.is_state(oCell.cell):
            continue
        for sPort, lNets in oCell.connections.items():
            if oFlat.direction(oCell, sPort) != "input":
                continue
            for oInput in lNets:
                if graph.is_variable(oInput) and oInput not in setSeen:
                    setSeen.add(oInput)
                    lWork.append(oInput)
    return lReturn
