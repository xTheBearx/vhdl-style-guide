# -*- coding: utf-8 -*-

from mhsg.design import netlist
from mhsg.design.rule import Finding, Rule, display_name, module_text

THROUGH_TYPES = {"$pos", "$buf"}


class rule_023(Rule):
    """
    This rule reports inout ports connected directly to an input or output port of the same module.

    .. NOTE:: This is a design rule. It runs in design analysis.

    An output port wired to a bidirectional port drives the bidirectional net with the value it reads, and an input
    port wired to it drives the net without a tri-state driver. In VHDL the modes of ports prevent most such
    connections; in Verilog an assign statement makes them.

    **Violation**

    .. code-block:: verilog

       module pad (inout wire pin, output wire value);
         assign value = pin;
       endmodule
    """

    def __init__(self):
        super().__init__()
        self.solution = "Read and drive the bidirectional port through a tri-state driver and an input buffer"

    def check_design(self, oContext):
        if oContext.netlist is None:
            return []
        lReturn = []
        for sModule, dModule in sorted(oContext.netlist.modules.items()):
            dPorts = dModule.get("ports", {})
            dInout = {}
            for sPort, dPort in dPorts.items():
                if dPort.get("direction") == "inout":
                    for oBit in dPort.get("bits", []):
                        if isinstance(oBit, int):
                            dInout.setdefault(oBit, sPort)
            if not dInout:
                continue
            # Buffers join nets too
            dSame = {}
            for dCell in dModule.get("cells", {}).values():
                if dCell.get("type") in THROUGH_TYPES:
                    dConnections = dCell.get("connections", {})
                    for oIn, oOut in zip(dConnections.get("A", []), dConnections.get("Y", [])):
                        if isinstance(oIn, int) and isinstance(oOut, int):
                            dSame.setdefault(oOut, oIn)
                            dSame.setdefault(oIn, oOut)
            setReported = set()
            for sPort, dPort in dPorts.items():
                sDirection = dPort.get("direction")
                if sDirection not in ("input", "output"):
                    continue
                for oBit in dPort.get("bits", []):
                    sInout = dInout.get(oBit) or dInout.get(dSame.get(oBit))
                    if sInout is None or (sInout, sPort) in setReported:
                        continue
                    setReported.add((sInout, sPort))
                    sFile, iLine = port_location(oContext, sModule, sPort)
                    if sFile is None:
                        # GHDL writes no locations on nets: the cells that drive the inout port, else any of the module
                        setInout = {b for b, s in dInout.items() if s == sInout}
                        lDrivers = [c for c, d in dModule.get("cells", {}).items() if any(b in setInout for b in d.get("connections", {}).get("Y", []))]
                        sFile, iLine = self.locate(oContext, sModule, lDrivers + list(dModule.get("cells", {})))
                    sMessage = f"Inout port {display_name(sInout)} of {module_text(sModule)} is connected directly to {sDirection} port {display_name(sPort)}"
                    lReturn.append(Finding(sFile, iLine, sMessage))
        return lReturn


def port_location(oContext, sModule, sPort):
    dNet = oContext.netlist.modules[sModule].get("netnames", {}).get(sPort, {})
    oLocation = netlist.source_location(dNet.get("attributes", {}).get("src"), getattr(oContext.netlist, "_setFiles", None))
    if oLocation is None:
        return None, 0
    return oContext.refine(oLocation, None)
