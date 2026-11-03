# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule


class rule_012(Rule):
    """
    This rule checks that every register has a reset.

    .. NOTE:: This is a lint rule. It runs in lint mode and implements DO-254 check SS14.

    A register is a signal assigned on the clock edge of a clocked process.
    It needs an assignment in the reset branch of that process, or the process needs a reset.
    Signals written through an index that is a name, such as :code:`mem(addr)`, are memories and are not checked.
    Registers without a reset on purpose, such as synchronizer flip-flops, should be justified.

    **Violation**

    .. code-block:: vhdl

       process (clk, reset) is
       begin
         if reset = '1' then
           out2 <= (others => '0');
         elsif rising_edge(clk) then
           out2 <= in2;
           out3 <= in1;
         end if;
       end process;

    **Fix**

    .. code-block:: vhdl

       process (clk, reset) is
       begin
         if reset = '1' then
           out2 <= (others => '0');
           out3 <= '0';
         elsif rising_edge(clk) then
           out2 <= in2;
           out3 <= in1;
         end if;
       end process;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Reset the register"

    def check(self, oModel, oFile):
        for oArchitecture in oModel.architectures:
            for oProcess in oArchitecture.processes:
                oClocking = oProcess.clock
                if oClocking is None:
                    continue
                setReset = {o.base for o in model.assignments(oClocking.reset_branch)}
                lReported = []
                for oAssignment in model.assignments(oClocking.clock_branch):
                    if not oAssignment.static_index or oAssignment.base in setReset or oAssignment.base in lReported:
                        continue
                    lReported.append(oAssignment.base)
                    if oClocking.reset is None or (oClocking.reset.style == "async" and not oClocking.reset_branch and oClocking.reset.name is None):
                        self.report(oFile, oAssignment.index, f"Register {oAssignment.base} has no reset; the process has none")
                    else:
                        sReset = oClocking.reset.name or "the reset"
                        self.report(oFile, oAssignment.index, f"Register {oAssignment.base} is not assigned when {sReset} is active")
