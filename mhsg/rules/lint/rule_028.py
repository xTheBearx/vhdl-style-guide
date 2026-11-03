# -*- coding: utf-8 -*-

from mhsg.lint.rule import Rule
from mhsg.rules.lint.rule_022 import visit


class rule_028(Rule):
    """
    This rule checks for variables in a combinational process that are read before they are written.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254 rule set (CP10).

    Such a variable keeps its value from the last time the process ran, so synthesis makes it a latch, or the
    simulation and the hardware differ. Assign the variable on every path before reading it.

    **Violation**

    .. code-block:: vhdl

       process (all) is
         variable sum : unsigned(7 downto 0);
       begin
         if enable = '1' then
           sum := a + b;
         end if;
         result <= sum;
       end process;

    **Fix**

    .. code-block:: vhdl

       process (all) is
         variable sum : unsigned(7 downto 0);
       begin
         sum := (others => '0');
         if enable = '1' then
           sum := a + b;
         end if;
         result <= sum;
       end process;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Assign the variable before reading it"

    def check(self, oModel, oFile):
        for oArchitecture in oModel.architectures:
            for oProcess in oArchitecture.processes:
                if oProcess.clock is not None or oProcess.has_wait or not oProcess.variables:
                    continue
                lReported = []
                visit(oProcess.statements, set(), oProcess.variables, lReported)
                for sName, iIndex in lReported:
                    self.report(oFile, iIndex, f"Variable {sName} is read before it is assigned on every path, so it keeps its last value like a latch")
