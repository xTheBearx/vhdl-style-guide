# -*- coding: utf-8 -*-

import re

from mhsg import language
from mhsg.design import flat, formal, fsm
from mhsg.design.rule import Finding, Rule, module_text
from mhsg.rules.design.rule_025 import assumption_values


class rule_047(Rule):
    """
    This rule reports states of state machines that can never be entered from reset, proven with SymbiYosys.

    .. NOTE:: This is a design rule. It runs in design analysis. It is disabled by default: it needs SymbiYosys, as in
              the YosysHQ OSS CAD Suite, and formal checks take longer than the other checks.

    A state machine is a register of two or more bits whose next value is only ever one of three or more constants,
    its states, or its own value, such as a signal of an enumerated type assigned in a case statement. The states are
    named after the values of the type, else numbered as the netlist encodes them. A state machine is checked when it
    starts from its reset state: an asynchronous reset, or a synchronous one, from a top input or a reset synchronizer.

    Each state is first looked for in a search of **depth** clock cycles from reset, 20 by default, which takes at
    most **cover_timeout** seconds, 300 by default. A state the search does not enter gets a proof of its own, which
    takes at most **timeout** seconds, 60 by default, for at most **maximum_proofs** checks, 20 by default, with
    those of design_048. A state proven never entered is reported; one neither entered nor proven is undecided, and
    reported when **report_undecided** is set. **assumptions** hold top inputs at a value in every cycle, as in
    :code:`[test_mode=0]`. Black boxes are taken out, and their outputs can take any value.

    This rule checks the states of the netlist through all of its logic, where lint_037 checks the assignments of a
    file: a state that an assignment enters, under a condition that is never true, is reported here.

    **Violation**

    .. code-block:: vhdl

       when RUN =>
         count <= count + 1;
         if count = 5 then
           state <= DONE;
         elsif count = 7 then    -- count never gets past 5 in RUN
           state <= ERROR;       -- ERROR is never entered
         end if;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.disabled_in_design = True
        self.solution = "Remove the state, or fix the logic that should enter it"
        self.depth = 20
        self.timeout = 60
        self.maximum_proofs = 20
        self.report_undecided = False
        self.cover_timeout = 300
        self.assumptions = []
        self.configuration.extend(["depth", "timeout", "cover_timeout", "maximum_proofs", "report_undecided", "assumptions"])

    def check_design(self, oContext):
        lMachines, iLeft, lErrors = state_machine_results(self, oContext)
        if lErrors:
            return lErrors
        lReturn = []
        for oMachine in lMachines:
            for iValue in oMachine.other_states():
                sStatus = oMachine.entered.get(iValue)
                sState = oMachine.state_name(iValue)
                if sStatus == formal.UNREACHABLE:
                    sMessage = f"State {sState} of {oMachine.name} in {module_text(oMachine.module)} proven never entered from reset"
                elif sStatus == formal.UNDECIDED and self.report_undecided:
                    sMessage = (
                        f"State {sState} of {oMachine.name} in {module_text(oMachine.module)} undecided: not entered within "
                        f"{self.depth} cycles, and not proven never entered within {self.timeout} s"
                    )
                else:
                    continue
                sFile, iLine = state_location(self, oContext, oMachine, iValue)
                lReturn.append(Finding(sFile, iLine, sMessage))
        if iLeft and self.report_undecided:
            sFile, iLine = top_location(self, oContext)
            lReturn.append(Finding(sFile, iLine, f"{iLeft} state checks not decided within {self.depth} cycles were not proven: more than maximum_proofs"))
        return lReturn


def state_machine_results(oRule, oContext):
    """
    Returns (the state machines with the results of formal.state_machine_checks, the checks left without a proof, a
    list of Findings for errors), computed once for the rules with the same settings.
    """
    if oContext.result is None or oContext.result.netlist is None or oContext.netlist is None:
        return [], 0, []
    sSby = formal.find_sby()
    if sSby is None:
        sFile, iLine = top_location(oRule, oContext)
        return [], 0, [Finding(sFile, iLine, "SymbiYosys (sby) is not installed: state machines are not checked")]
    dAssumptions = assumption_values(oRule.assumptions)
    tKey = (int(oRule.depth), int(oRule.timeout), int(oRule.maximum_proofs), int(oRule.cover_timeout), tuple(sorted(dAssumptions.items())))
    dCache = oContext.__dict__.setdefault("_dStateMachines", {})
    if tKey not in dCache:
        lMachines, iLeft, sError = formal.state_machine_checks(
            sSby,
            oContext.result.netlist,
            flat.top_module(oContext.netlist),
            oContext.flat(),
            set(oContext.netlist.black_boxes),
            int(oRule.depth),
            int(oRule.timeout),
            int(oRule.maximum_proofs),
            dAssumptions,
            int(oRule.cover_timeout),
        )
        for oMachine in lMachines:
            name_states(oContext, oMachine)
        dCache[tKey] = (lMachines, iLeft, sError)
    lMachines, iLeft, sError = dCache[tKey]
    if sError is not None:
        sFile, iLine = top_location(oRule, oContext)
        return [], 0, [Finding(sFile, iLine, f"State machines are not checked: {sError}")]
    return lMachines, iLeft, []


def name_states(oContext, oMachine):
    """Names the states of a state machine from the attributes of the netlist, else from the VHDL."""
    fsm.attribute_names(oMachine, oContext.netlist.modules.get(oMachine.module, {}))
    if oMachine.names:
        return
    oLocation = oContext.netlist.location(oMachine.module, oMachine.cell)
    lFiles = oContext.design.all_files() if oContext.design is not None else []
    sFile = oLocation.file if oLocation is not None else None
    fsm.vhdl_names(oMachine, lFiles, sFile)
    if not oMachine.names:
        fsm.sv_names(oMachine, lFiles, sFile)


def state_location(oRule, oContext, oMachine, iValue):
    """
    The location of a state: the assignment that enters it, the first line of the process of the logic that loads it
    that assigns the name of the state to a signal or variable, else the first assignment of the signal there, else
    the register.
    """
    lCells = oMachine.states.get(iValue, []) + [oMachine.cell]
    sFile, iLine = oRule.locate(oContext, oMachine.module, lCells)
    if sFile is None or language.is_verilog(sFile):
        # Yosys locates the logic of Verilog at the assignment itself
        return (sFile, iLine) if sFile is not None else oRule.locate(oContext, oMachine.module, lCells, oMachine.signal)
    sName = oMachine.names.get(iValue)
    lArchitectures = oContext.vhdl_summary(sFile) if sName else None
    if not lArchitectures:
        return oRule.locate(oContext, oMachine.module, lCells, oMachine.signal)
    reAssignment = re.compile(r"(?:<=|:=)\s*" + re.escape(sName) + r"\b", re.IGNORECASE)
    try:
        with open(sFile, encoding="utf-8", errors="replace") as oFile:
            lLines = oFile.read().splitlines()
    except OSError:
        return sFile, iLine
    for oArchitecture in lArchitectures:
        for oProcess in oArchitecture.processes:
            if not oProcess.line <= iLine <= oProcess.end_line:
                continue
            for iAssignment in range(oProcess.line, min(oProcess.end_line, len(lLines)) + 1):
                if reAssignment.search(lLines[iAssignment - 1].split("--")[0]):
                    return sFile, iAssignment
    return oRule.locate(oContext, oMachine.module, lCells, oMachine.signal)


def top_location(oRule, oContext):
    sTop = flat.top_module(oContext.netlist)
    return oRule.locate(oContext, sTop, list(oContext.netlist.modules.get(sTop, {}).get("cells", {})))
