# -*- coding: utf-8 -*-

from mhsg.design.rule import Finding, Rule, module_text


class rule_044(Rule):
    """
    This rule checks that the net an output port of an instance drives has the name of that port in the module that
    holds the instance.

    .. NOTE:: This is a design rule. It runs in design analysis. It is disabled by default: a design need not follow
              it.

    A signal that keeps its name from the output that drives it to the inputs that read it can be followed through the
    hierarchy by name, in the code, in simulation and in the netlist. Outputs left open or tied to a constant are not
    checked; black boxes are not checked.

    **Violation**

    .. code-block:: vhdl

       u_fifo : entity work.fifo port map (empty => fifo_is_empty, ...);

    **Fix**

    .. code-block:: vhdl

       u_fifo : entity work.fifo port map (empty => empty, ...);
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.disabled_in_design = True
        self.solution = "Name the net after the output port that drives it"

    def check_design(self, oContext):
        oNetlist = oContext.netlist
        if oNetlist is None:
            return []
        dModules = oNetlist.modules
        lReturn = []
        for sModule, dModule in sorted(dModules.items()):
            for sCell, dCell in sorted(dModule.get("cells", {}).items()):
                sType = dCell.get("type")
                if sType not in dModules:
                    continue
                dPorts = dModules[sType].get("ports", {})
                dWrong = {}
                for sPort, lBits in sorted(dCell.get("connections", {}).items()):
                    if dPorts.get(sPort, {}).get("direction") != "output":
                        continue
                    lInts = [b for b in lBits if isinstance(b, int)]
                    if not lInts:
                        continue
                    sName = sPort.lstrip("\\")
                    lNames = [s.lstrip("\\") for s in oNetlist.bit_names(sModule, lInts[0]) if not s.startswith("$")]
                    if lNames and not any(same_name(sName, s) for s in lNames):
                        # The fields of a record port are one port
                        dWrong.setdefault(sName.split(".")[0], lNames[0].split(".")[0].split("[")[0])
                lWrong = [f"{s} drives {n}" for s, n in dWrong.items()]
                if lWrong:
                    sFile, iLine = self.locate(oContext, sModule, [sCell])
                    sInstance = sCell.lstrip("\\")
                    lReturn.append(
                        Finding(sFile, iLine, f"Outputs of instance {sInstance} in {module_text(sModule)} drive nets of other names: {'; '.join(lWrong)}"),
                    )
        return lReturn


def same_name(sPort, sNet):
    """
    Whether a net has the name of a port: the same name, or the same field of a record of the same name, also in a
    generate statement, whose label comes before the name, and as a bit or a slice.
    """
    sPort = sPort.lower()
    sNet = sNet.lower().split("[")[0].split("(")[0]
    if sNet == sPort or sNet.endswith("." + sPort):
        return True
    sBase = sPort.split(".")[0]
    return sNet == sBase or sNet.endswith("." + sBase) or sNet.split(".")[-1] == sBase
