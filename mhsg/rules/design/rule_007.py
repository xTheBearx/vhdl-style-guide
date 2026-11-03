# -*- coding: utf-8 -*-

from mhsg.design import graph
from mhsg.design.rule import Finding, Rule, display_name, module_text


class rule_007(Rule):
    """
    This rule reports combinational paths with more logic levels than :code:`maximum_depth` in the synthesized design.

    .. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check SS19.

    A path starts at a register, a memory or an input of the design, and ends at a register, a memory or an output of the design.
    Paths through instances of other entities are counted in full, and each path is reported once: in the entity that holds the deepest part.
    The depth counts the operators before synthesis maps them to the device: an adder, a comparison or a multiplexer is one level,
    inverters count nothing, and a chain of the same and, or or xor operator counts once.
    Long chains of if and elsif branches, and loops unrolled into chains of multiplexers, are the usual causes.
    Each register is reported once, with its deepest path.

    **Violation**

    .. code-block:: vhdl

       -- With maximum_depth set to 2
       result <= (a + b) + (c + d) when sel = '1' else (others => '0');
    """

    def __init__(self):
        super().__init__()
        self.solution = "Split the path with a register"
        self.maximum_depth = 48
        self.configuration.append("maximum_depth")

    def check_design(self, oContext):
        oGraph = oContext.graph()
        if oGraph is None:
            return []
        lReturn = []
        setInstantiated = {d.get("type") for m in oGraph.netlist.modules.values() for d in m.get("cells", {}).values()}
        for sModule in oGraph.modules():
            oModule = oGraph.graph(sModule)
            bTop = sModule not in setInstantiated
            dDepths = oModule.depths()
            dWorst = {}
            for sCell, iBit, iExtra in oModule.endpoints():
                if iExtra > int(self.maximum_depth):
                    # The path is too deep inside the instance alone, which is reported in its entity
                    continue
                iDepth = start_depth(dDepths, iBit) + iExtra
                if iDepth > int(self.maximum_depth) and iDepth > dWorst.get(sCell, (-1,))[0]:
                    dWorst[sCell] = (iDepth, iBit)
            if bTop:
                for sPort, dPort in oModule.ports.items():
                    if dPort.get("direction") not in ("output", "inout"):
                        continue
                    for oBit in dPort.get("bits", []):
                        if isinstance(oBit, int):
                            iDepth = start_depth(dDepths, oBit)
                            if iDepth > int(self.maximum_depth) and iDepth > dWorst.get("port " + sPort, (-1,))[0]:
                                dWorst["port " + sPort] = (iDepth, oBit)
            for sEnd, (iDepth, iBit) in sorted(dWorst.items()):
                lReturn.append(self.finding(oContext, oModule, sEnd, iDepth, iBit))
        return lReturn

    def finding(self, oContext, oModule, sEnd, iDepth, iBit):
        sModule = module_text(oModule.name)
        if sEnd.startswith("port "):
            sCell = oModule.driving_cell(iBit)
            sFile, iLine = self.locate(oContext, oModule.name, [sCell] if sCell else [], sEnd[5:])
            return Finding(sFile, iLine, f"Path of {iDepth} logic levels to output {sEnd[5:]} of {sModule}, more than {self.maximum_depth}")
        if oModule.is_instance(sEnd):
            sFile, iLine = self.locate(oContext, oModule.name, [sEnd])
            return Finding(sFile, iLine, f"Path of {iDepth} logic levels into instance {display_name(sEnd)} in {sModule}, more than {self.maximum_depth}")
        lQ = oModule.cells[sEnd].get("connections", {}).get("Q") or oModule.cells[sEnd].get("connections", {}).get("DATA") or []
        sName = display_name(oModule.bit_name(lQ[0])) if lQ and isinstance(lQ[0], int) else None
        sFile, iLine = self.locate(oContext, oModule.name, [sEnd], sName)
        sTarget = f"register {sName}" if sName and not sName.startswith("$") else "a register"
        return Finding(sFile, iLine, f"Path of {iDepth} logic levels to {sTarget} in {sModule}, more than {self.maximum_depth}")


def start_depth(dDepths, iBit):
    """
    The depth of the deepest path to a bit, from a register or an input of the entity. A path from an input
    continues outside, where the instantiating entity adds its part if the part inside is within the limit.
    """
    iLaunch, iPass = dDepths.get(iBit, (graph.NO_DEPTH, graph.NO_DEPTH))
    return max(iLaunch, iPass)
