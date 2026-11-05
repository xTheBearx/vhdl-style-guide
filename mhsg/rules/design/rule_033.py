# -*- coding: utf-8 -*-

from mhsg.design import control, graph
from mhsg.design.rule import Finding, Rule

# The roles of black box inputs made to take each kind of net
ALLOWED = {control.CLOCK: ("clock",), control.RESET: ("reset_in",), control.TRISTATE: ()}


class rule_033(Rule):
    """
    This rule reports clocks, asynchronous resets and tri-state outputs connected to inputs of black boxes that are not
    declared to take them.

    .. NOTE:: This is a design rule. It runs in design analysis. It is disabled by default: it needs every black box
              declared, see the black boxes of :doc:`design_analysis`.

    Inside a black box, design analysis cannot follow a clock, a reset or a tri-state bus, and scan test cannot
    control it. An input declared as a clock or a reset of the box, or named by another of its roles, such as the
    input of a buffer, is made for it and not reported.

    **Violation**

    The clock connected to a data input of a vendor IP.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.disabled_in_design = True
        self.solution = "Connect clocks and resets only to inputs declared for them, and keep tri-state buses out of black boxes"

    def check_design(self, oContext):
        oAnalysis = oContext.cdc()
        if oAnalysis is None:
            return []
        oFlat = oAnalysis.flat
        setClocks = {o.net for o in oAnalysis.clocks.values() if graph.is_variable(o.net)}
        setResets = {o for o in control.reset_roots(oAnalysis) if graph.is_variable(o)}
        lReturn = []
        for oBox in oFlat.cells:
            if not oBox.is_black_box():
                continue
            oInstance = oAnalysis.boxes.get(id(oBox))
            for sPort, lNets in sorted(oBox.connections.items()):
                if oFlat.direction(oBox, sPort) != "input":
                    continue
                oRole = oAnalysis.box_role(oBox, sPort)
                bReferenced = oInstance is not None and oInstance.referenced(sPort)
                for oNet in lNets:
                    if not graph.is_variable(oNet):
                        continue
                    sKind = self.kind(oAnalysis, oNet, setClocks, setResets)
                    if sKind is None or bReferenced or (oRole is not None and oRole.kind in ALLOWED[sKind]):
                        continue
                    sFile, iLine = oContext.locate_cell(oBox)
                    sName = oFlat.net_name(oAnalysis.through_transparent(oNet)[0])
                    sKindText = "Tri-state output" if sKind == control.TRISTATE else sKind.capitalize()
                    lReturn.append(Finding(sFile, iLine, f"{sKindText} {sName} is connected to input {sPort} of black box {oBox!r}"))
                    break
        return lReturn

    @staticmethod
    def kind(oAnalysis, oNet, setClocks, setResets):
        oRoot = oAnalysis.through_transparent(oNet)[0]
        if oRoot in setClocks:
            return control.CLOCK
        if oRoot in setResets:
            return control.RESET
        tDriver = oAnalysis.flat.driver(oNet)
        if tDriver is not None and tDriver[0] is not None and tDriver[0].type in control.TRISTATE_ENABLES:
            return control.TRISTATE
        return None
