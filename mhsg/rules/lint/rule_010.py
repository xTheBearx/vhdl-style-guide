# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule, unit_ports


class rule_010(Rule):
    """
    This rule checks that a signal is driven by only one process, concurrent assignment or instance in an architecture.

    .. NOTE:: This is a lint rule. It runs in lint mode and implements DO-254 check SS6.

    Several drivers of the same signal conflict in hardware.
    Different fixed parts of a signal, such as :code:`a(0)` and :code:`a(1)`, may be driven separately.
    Drivers are only compared when they are in the same branches of the same if and case generate statements,
    since which generate statements exist depends on generics; design analysis checks the elaborated design.
    A part selected by a name, such as :code:`mem(addr)`, is not checked.

    **Violation**

    .. code-block:: vhdl

       operate_proc : process (a1) is
       begin
         a3 <= a1 and "10101000";
       end process;

       test_proc : process (a2) is
       begin
         a3 <= a2;
       end process;

    **Fix**

    .. code-block:: vhdl

       operate_proc : process (a1, a2) is
       begin
         a3 <= (a1 and "10101000") or a2;
       end process;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Drive the signal from one place"

    def check(self, oModel, oFile):
        for oArchitecture in oModel.architectures:
            dDrivers = {}
            oDeclarations = oFile.get_declarations()
            for oDriver in drivers(oArchitecture, oFile):
                # Signals of the same name declared in different blocks or generate statements are different signals
                lDeclarations = oDeclarations.find(oDriver.base, oDriver.index)
                oKey = lDeclarations[0].index if lDeclarations else oDriver.base
                dDrivers.setdefault(oKey, []).append(oDriver)
            for lDrivers in dDrivers.values():
                for iDriver, oDriver in enumerate(lDrivers):
                    for oOther in lDrivers[:iDriver]:
                        if (
                            oOther.owner is not oDriver.owner
                            and model.same_conditional_generates(oOther.generate, oDriver.generate, oModel.dGenerateConditions)
                            and conflict(oOther, oDriver)
                        ):
                            self.report(oFile, oDriver.index, f"Signal {oDriver.target} is also driven by {oOther.description} on line {oOther.line}")
                            break


class Driver:
    def __init__(self, oOwner, sDescription, sTarget, sBase, bIndexed, bStatic, iIndex, iLine):
        self.generate = oOwner.generate
        self.owner = oOwner
        self.description = sDescription
        self.target = sTarget
        self.base = sBase
        self.indexed = bIndexed
        self.static = bStatic
        self.index = iIndex
        self.line = iLine


def drivers(oArchitecture, oFile):
    """Returns one Driver for each target assigned by each process, concurrent assignment and instance output."""
    lReturn = []
    for oProcess in oArchitecture.processes:
        sDescription = "process " + oProcess.label if oProcess.label else "the process"
        dSeen = {}
        for oAssignment in model.assignments(oProcess.statements):
            if oAssignment.target not in dSeen:
                dSeen[oAssignment.target] = True
                lReturn.append(
                    Driver(
                        oProcess,
                        sDescription,
                        oAssignment.target,
                        oAssignment.base,
                        oAssignment.indexed,
                        oAssignment.static_index,
                        oAssignment.index,
                        oAssignment.line,
                    ),
                )
    for oAssignment in oArchitecture.assignments:
        lReturn.append(
            Driver(
                oAssignment,
                "a concurrent assignment",
                oAssignment.target,
                oAssignment.base,
                oAssignment.indexed,
                oAssignment.static_index,
                oAssignment.index,
                oAssignment.line,
            ),
        )
    for oInstance in oArchitecture.instances:
        lPorts = unit_ports(oFile, oInstance) or []
        dModes = dict(lPorts)
        for iPosition, (sFormal, sActual, iLine) in enumerate(oInstance.associations):
            sPort = sFormal if sFormal is not None else (lPorts[iPosition][0] if iPosition < len(lPorts) else None)
            if dModes.get(sPort) in ("out", "inout", "buffer") and sActual != "open" and model.reName.match(sActual or ""):
                lReturn.append(
                    Driver(oInstance, "instance " + oInstance.label, sActual, model.base_name(sActual), "." in sActual, True, oInstance.index, iLine),
                )
    return lReturn


def conflict(oFirst, oSecond):
    """Returns True if two drivers of the same signal can drive the same part of it."""
    if not oFirst.static or not oSecond.static:
        return False
    if not oFirst.indexed or not oSecond.indexed:
        return True
    return oFirst.target == oSecond.target
