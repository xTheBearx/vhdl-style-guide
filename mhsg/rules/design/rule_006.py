# -*- coding: utf-8 -*-

import re

from mhsg.design.rule import Finding, Rule, display_name, module_text


class rule_006(Rule):
    """
    This rule reports registers that are never used, and signals that are read but never assigned, in the elaborated design.

    .. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check SS17.

    A register is unused when its value reaches no output of the entity, no instance that uses it, and no memory that is read,
    so the register and the logic that feeds only it are unused.
    A black box uses its inputs when one of its outputs is used, or when it has no outputs, such as a debug core.
    Each entity is checked on its own, so an output that the instantiating entity leaves unconnected does not make the logic behind it unused;
    lint_004 reports such outputs.
    Unused combinational signals are not reported, since synthesis rewrites them; the registers they feed are.
    GHDL removes a register that nothing reads, so a signal that a clocked process assigns but that is missing from the netlist is reported too.
    A signal that is read but never assigned is reported at its declaration.

    **Violation**

    .. code-block:: vhdl

       process (clk) is
       begin
         if rising_edge(clk) then
           count <= count + 1;  -- count is not read anywhere
         end if;
       end process;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Remove the unused logic"

    def check_design(self, oContext):
        oGraph = oContext.graph()
        if oGraph is None:
            return []
        lReturn = []
        lSeen = []

        def add(sFile, iLine, sMessage, tKey=None):
            tKey = tKey or (sFile, iLine, sMessage)
            if tKey not in lSeen:
                lSeen.append(tKey)
                lReturn.append(Finding(sFile, iLine, sMessage))

        for sModule in oGraph.modules():
            oModule = oGraph.graph(sModule)
            setLive = oModule.live_bits()
            for sName, lBits in sorted(oModule.named_nets()):
                if lBits:
                    for lCells, sMessage in self.check_net(oModule, setLive, sName, lBits):
                        sFile, iLine = self.locate(oContext, sModule, lCells, display_name(sName))
                        add(sFile, iLine, sMessage)
            for sFile, iLine, sName in removed_registers(oContext, oModule):
                add(sFile, iLine, f"Register {sName} in {module_text(sModule)} is never used", (sFile, iLine, sName))
            for sFile, iLine, sName in unassigned_signals(oContext, oModule):
                add(sFile, iLine, f"Signal {sName} in {module_text(sModule)} is read but never assigned", (sFile, iLine, sName))
        return lReturn

    def check_net(self, oModule, setLive, sName, lBits):
        sText = f"{display_name(sName)} in {module_text(oModule.name)}"
        lDrivers = [t for b in lBits for t in oModule.drivers.get(b, [])]
        lCells = sorted({t[0] for t in lDrivers if t[0] is not None})
        if not lDrivers:
            lReaders = sorted({t[0] for b in lBits for t in oModule.readers.get(b, []) if t[0] is not None and b in setLive})
            if lReaders:
                return [(lReaders, f"Signal {sText} is read but never assigned")]
            return []
        if any(b in setLive for b in lBits) or any(t[0] is None or oModule.is_instance(t[0]) for t in lDrivers):
            return []
        # Synthesis folds combinational logic, which can leave unused copies of signals the VHDL uses: only registers count
        if not all(oModule.is_state(s) for s in lCells):
            return []
        return [(lCells, f"Register {sText} is never used")]


def module_lines(oContext, oModule):
    """Returns {file: set of lines} of the cells of a module that have a location."""
    dReturn = {}
    for sCell in oModule.cells:
        oLocation = oContext.netlist.location(oModule.name, sCell)
        if oLocation is not None:
            dReturn.setdefault(oLocation.file, set()).add(oLocation.line)
    return dReturn


def netlist_names(oModule):
    """Returns the lower case names of the signals and memories in the netlist of a module, and each part of their dotted names."""
    setReturn = set()
    lNames = list(oModule.module.get("netnames", {}))
    lNames += [str(d.get("parameters", {}).get("MEMID", "")) for d in oModule.cells.values()]
    lNames += list(oModule.module.get("memories", {}))
    for sName in lNames:
        for sPart in display_name(sName).lower().split("[")[0].split("."):
            setReturn.add(sPart)
    return setReturn


def removed_registers(oContext, oModule):
    """
    Yields (file, line, name) for the signals that a clocked process assigns but that are not in the netlist.
    GHDL removes a register that nothing reads. Only processes with logic in the netlist are checked, since a
    process in a generate statement that is not elaborated has none.
    """
    setNames = netlist_names(oModule)
    for sFile, setLines in module_lines(oContext, oModule).items():
        lArchitectures = oContext.vhdl_summary(sFile)
        if lArchitectures is None:
            continue
        for oArchitecture in lArchitectures:
            for oProcess in oArchitecture.processes:
                if not oProcess.clocked or not any(oProcess.line <= i <= oProcess.end_line for i in setLines):
                    continue
                lDone = []
                for sBase, iLine in oProcess.assignments:
                    if sBase in lDone or sBase in setNames:
                        continue
                    lDone.append(sBase)
                    yield sFile, iLine, sBase


reSignal = re.compile(r"^\s*signal\s+([^:]+):", re.IGNORECASE)


def unassigned_signals(oContext, oModule):
    """
    Yields (file, line, name) for the signals of a module that GHDL replaced by an unknown value: signals that
    are never assigned and have no initial value. The line is that of the declaration.
    """
    lNames = [
        s
        for s, d in oModule.module.get("netnames", {}).items()
        if not s.startswith("$") and s not in oModule.ports and d.get("bits") and all(b == "x" for b in d["bits"])
    ]
    if not lNames:
        return
    for sFile in module_lines(oContext, oModule):
        try:
            with open(sFile, encoding="utf-8", errors="replace") as oFile:
                lLines = oFile.readlines()
        except OSError:
            continue
        for sName in lNames:
            sBase = display_name(sName).split(".")[-1].lower()
            for iLine, sLine in enumerate(lLines, 1):
                oMatch = reSignal.match(sLine.split("--")[0])
                if oMatch and sBase in [s.strip().lower() for s in oMatch.group(1).split(",")]:
                    yield sFile, iLine, display_name(sName)
                    break
