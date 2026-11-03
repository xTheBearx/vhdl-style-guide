# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule, signal_kind


class rule_002(Rule):
    """
    This rule checks that the sensitivity list of a process contains the signals the process needs, and no others.

    .. NOTE:: This is a lint rule. It runs in lint mode and implements DO-254 check CP8.

    A combinational process needs every signal it reads; a missing signal makes simulation differ from the synthesized hardware.
    A clocked process needs only its clock and the signals tested before the clock edge, such as an asynchronous reset.
    Processes with :code:`process (all)` or a wait statement are not checked.
    Names declared outside the file, other than the ports of the entity, cannot be told apart from constants and are not reported missing.

    **Violation**

    .. code-block:: vhdl

       process (clk, rcv_bit_cnt) is
       begin
         if rst = '0' then
           rcv_state <= waiting;
         elsif falling_edge(clk) then
           rcv_state <= rcv_next_state;
         end if;
       end process;

    **Fix**

    .. code-block:: vhdl

       process (clk, rst) is
       begin
         if rst = '0' then
           rcv_state <= waiting;
         elsif falling_edge(clk) then
           rcv_state <= rcv_next_state;
         end if;
       end process;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Correct the sensitivity list"

    def check(self, oModel, oFile):
        for oArchitecture in oModel.architectures:
            for oProcess in oArchitecture.processes:
                if not isinstance(oProcess.sensitivity, list) or oProcess.has_wait:
                    continue
                if oProcess.clock is not None:
                    self.check_clocked(oArchitecture, oProcess, oFile)
                elif not model.has_edge(oProcess):
                    self.check_combinational(oArchitecture, oProcess, oFile)

    def check_clocked(self, oArchitecture, oProcess, oFile):
        oClocking = oProcess.clock
        lControls = unique(s.split(".")[0] for lCondition in oClocking.async_conditions for s in model.names(lCondition))
        # The reset is needed unless it is known not to be a signal; other names tested only if they are known signals
        sReset = oClocking.reset.name if oClocking.reset is not None else None
        lNeeded = [oClocking.name]
        for sName in lControls:
            sKind = signal_kind(oFile, oArchitecture, sName, oProcess.index)
            if sKind in ("signal", "port") or (sName == sReset and sKind is None):
                lNeeded.append(sName)
        for sName in unique(lNeeded):
            if sName not in oProcess.sensitivity:
                self.report(oFile, oProcess.index, f"Add {sName} to the sensitivity list")
        for sName in unique(oProcess.sensitivity):
            if sName != oClocking.name and sName not in lControls:
                self.report(oFile, oProcess.index, f"Remove {sName} from the sensitivity list of the clocked process")

    def check_combinational(self, oArchitecture, oProcess, oFile):
        lReads = unique(model.reads(oProcess.statements))
        lLoopParameters = [o.parameter for o in model.walk(oProcess.statements) if isinstance(o, model.Loop)]
        lReported = []
        for sRead in lReads:
            sName = sRead.split(".")[0]
            if sName in oProcess.variables or sName in lLoopParameters or sName in lReported:
                continue
            # A record field is covered by the record, or by the field itself, in the list
            if any(sRead == s or sRead.startswith(s + ".") for s in oProcess.sensitivity):
                continue
            if signal_kind(oFile, oArchitecture, sName, oProcess.index) in ("signal", "port"):
                lReported.append(sName)
                self.report(oFile, oProcess.index, f"Add {sRead} to the sensitivity list; the process reads it")
        for sName in unique(oProcess.sensitivity):
            if not any(model.overlaps(sName, s) for s in lReads):
                self.report(oFile, oProcess.index, f"Remove {sName} from the sensitivity list; the process does not read it")


def unique(lNames):
    lReturn = []
    for sName in lNames:
        if sName not in lReturn:
            lReturn.append(sName)
    return lReturn
