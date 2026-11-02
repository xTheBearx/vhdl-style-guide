# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule


class rule_008(Rule):
    """
    This rule checks for combinational feedback: a signal that is read and assigned in the same combinational process or concurrent assignment.

    .. NOTE:: This is a lint rule. It runs in lint mode and implements DO-254 check SS3.

    Such a signal forms a loop without a register, whose behaviour is unpredictable.
    Assignments to an element or slice, such as :code:`p(i) <= p(i - 1)`, are not checked, since they may read other elements.
    Loops through several processes or assignments are not detected.

    **Violation**

    .. code-block:: vhdl

       fred_s <= gated_in_s or pulse_r;

       process (en_i, fred_s) is
       begin
         gated_in_s <= fred_s and en_i;
         if en_i = '0' then
           gated_in_s <= not gated_in_s;
         end if;
       end process;

    **Fix**

    .. code-block:: vhdl

       process (clk) is
       begin
         if rising_edge(clk) then
           gated_in_r <= not gated_in_r;
         end if;
       end process;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Break the combinational loop"

    def check(self, oModel, oFile):
        for oArchitecture in oModel.architectures:
            for oProcess in oArchitecture.processes:
                if not model.is_combinational(oProcess):
                    continue
                lReads = model.reads(oProcess.statements)
                lReported = []
                for oAssignment in model.assignments(oProcess.statements):
                    if "(" in oAssignment.target or oAssignment.path in lReported or not any(model.overlaps(oAssignment.path, s) for s in lReads):
                        continue
                    lReported.append(oAssignment.path)
                    self.report(oFile, oAssignment.index, f"Signal {oAssignment.path} is assigned and read in the same combinational process")
            for oAssignment in oArchitecture.assignments:
                if oAssignment.clocked or "(" in oAssignment.target:
                    continue
                if any(model.overlaps(oAssignment.path, s) for s in oAssignment.value_reads):
                    self.report(oFile, oAssignment.index, f"Signal {oAssignment.path} is assigned from an expression that reads it")
