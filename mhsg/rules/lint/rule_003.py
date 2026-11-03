# -*- coding: utf-8 -*-

from mhsg.lint.rule import Rule, unit_ports


class rule_003(Rule):
    """
    This rule checks that every input port of an instance is connected.

    .. NOTE:: This is a lint rule. It runs in lint mode and implements DO-254 check CP11.

    An input or inout port that is missing from the port map, or mapped to :code:`open`, is left floating or takes its default value.
    The ports of the instantiated unit are taken from the file or from the other files of the run.
    Instances of units whose ports are not known are not checked.

    **Violation**

    .. code-block:: vhdl

       u_bad : usable_vhd
         port map (
           in1  => d,
           out1 => q1,
           out2 => q2
         );

    **Fix**

    .. code-block:: vhdl

       u_bad : usable_vhd
         port map (
           in1  => d,
           in2  => addr,
           out1 => q1,
           out2 => q2
         );
    """

    lModes = ("in", "inout")
    sKind = "Input"

    def __init__(self):
        super().__init__()
        self.solution = "Connect the input port"

    def check(self, oModel, oFile):
        for oArchitecture in oModel.architectures:
            for oInstance in oArchitecture.instances:
                lPorts = unit_ports(oFile, oInstance)
                if not lPorts:
                    continue
                dConnected = connections(oInstance, lPorts)
                for sPort, sMode in lPorts:
                    if sMode in self.lModes and dConnected.get(sPort, "open") == "open":
                        self.report(oFile, oInstance.index, f"{self.sKind} port {sPort} of instance {oInstance.label} is not connected")


def connections(oInstance, lPorts):
    """Returns the actual of each connected port of an instance by port name; positional associations follow the port order."""
    dReturn = {}
    for iPosition, (sFormal, sActual, _) in enumerate(oInstance.associations):
        if sFormal is None:
            if iPosition < len(lPorts):
                dReturn[lPorts[iPosition][0]] = sActual
        elif sActual != "open" or sFormal not in dReturn:
            # A port connected in parts, such as d(0) => a, d(1) => open, counts as connected
            dReturn[sFormal] = sActual
    return dReturn
