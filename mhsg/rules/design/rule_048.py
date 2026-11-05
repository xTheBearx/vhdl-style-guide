# -*- coding: utf-8 -*-

from mhsg.design import formal
from mhsg.design.rule import Finding, Rule, module_text
from mhsg.rules.design.rule_047 import (
    state_location,
    state_machine_results,
    top_location,
)


class rule_048(Rule):
    """
    This rule reports state machines that lock up: states after which the machine never returns to its reset state,
    whatever its inputs do, proven with SymbiYosys.

    .. NOTE:: This is a design rule. It runs in design analysis. It is disabled by default: it needs SymbiYosys, as in
              the YosysHQ OSS CAD Suite, and formal checks take longer than the other checks.

    The state machines are those of design_047. For each state the machine enters, a search of **depth** clock cycles
    from reset, 20 by default, which takes at most **cover_timeout** seconds, 300 by default, looks for a return to
    the reset state after it. A state the search finds no return from gets a proof that the machine never returns
    after it, which takes at most **timeout** seconds, 60 by default, for at most **maximum_proofs** checks, 20 by
    default, after those of the states of design_047. The states proven without a return are reported in one finding
    per state machine: a state that is never left, or states the machine only moves between. A state neither shown to
    return nor proven not to is undecided, and reported when **report_undecided** is set. **assumptions** hold top
    inputs at a value in every cycle, as in :code:`[test_mode=0]`.

    A state machine that some inputs keep from returning, such as one waiting for an acknowledge that never comes, is
    not reported: the check is that no inputs at all bring it back. A state machine whose reset state no state returns
    to is not checked either: its reset state is a start-up state, left once, such as a transmitter that waits in
    Reset_s after reset and then moves between Idle_s and Data_s. Only a machine with a state shown to return to the
    reset state, so that the reset state is part of its cycle, is reported.

    **Violation**

    .. code-block:: vhdl

       when WAIT_ACK =>
         if ack = '1' then
           state <= HOLD;
         end if;
       when HOLD =>
         state <= WAIT_ACK;     -- WAIT_ACK and HOLD never return to IDLE
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.disabled_in_design = True
        self.solution = "Add a way back to the reset state"
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
            sMachine = f"{oMachine.name} in {module_text(oMachine.module)}"
            sReset = oMachine.state_name(oMachine.reset)
            lLocked = [i for i in oMachine.other_states() if oMachine.returns.get(i) == formal.UNREACHABLE]
            # A reset state that no state returns to is a start-up state, left once: the machine is not checked
            bCycle = any(oMachine.returns.get(i) == formal.REACHABLE for i in oMachine.other_states())
            if lLocked and bCycle:
                sStates = ", ".join(oMachine.state_name(i) for i in lLocked)
                sFile, iLine = state_location(self, oContext, oMachine, lLocked[0])
                sWord = "state" if len(lLocked) == 1 else "states"
                lReturn.append(Finding(sFile, iLine, f"State machine {sMachine} never returns to its reset state {sReset} after {sWord} {sStates}"))
            lUndecided = [i for i in oMachine.other_states() if oMachine.returns.get(i) == formal.UNDECIDED]
            if lUndecided and self.report_undecided:
                sStates = ", ".join(oMachine.state_name(i) for i in lUndecided)
                sFile, iLine = state_location(self, oContext, oMachine, lUndecided[0])
                lReturn.append(
                    Finding(
                        sFile,
                        iLine,
                        f"State machine {sMachine} undecided: no return to {sReset} found within {self.depth} cycles after {sStates}, "
                        f"and none proven impossible within {self.timeout} s",
                    ),
                )
        if iLeft and self.report_undecided:
            sFile, iLine = top_location(self, oContext)
            lReturn.append(Finding(sFile, iLine, f"{iLeft} state checks not decided within {self.depth} cycles were not proven: more than maximum_proofs"))
        return lReturn
