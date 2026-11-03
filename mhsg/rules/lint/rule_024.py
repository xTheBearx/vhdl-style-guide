# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule


class rule_024(Rule):
    """
    This rule checks that a combinational process gives every signal it assigns a default value at its start.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254_plus rule set.

    A default assignment before the if and case statements makes sure every path assigns the signal, so no latch can be inferred,
    and shows the value of the signal when no branch changes it.

    **Violation**

    .. code-block:: vhdl

       process (all) is
       begin
         case state is
           when IDLE => state_next <= START;
           when others => state_next <= IDLE;
         end case;
       end process;

    **Fix**

    .. code-block:: vhdl

       process (all) is
       begin
         state_next <= state;
         case state is
           when IDLE => state_next <= START;
           when others => state_next <= IDLE;
         end case;
       end process;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Assign a default value at the start of the process"

    def check(self, oModel, oFile):
        for oArchitecture in oModel.architectures:
            for oProcess in oArchitecture.processes:
                if not model.is_combinational(oProcess):
                    continue
                lDefaults = [o for o in oProcess.statements if isinstance(o, model.Assignment) and o.kind == "signal"]
                lReported = []
                for oStatement in oProcess.statements:
                    if isinstance(oStatement, model.Assignment):
                        continue
                    for oAssignment in model.assignments([oStatement]):
                        sPart = oAssignment.covers()
                        setBefore = {o.covers() for o in lDefaults if o.index < oAssignment.index}
                        if not model.covered(sPart, setBefore) and sPart not in lReported:
                            lReported.append(sPart)
                            self.report(oFile, oAssignment.index, f"Give {sPart} a default value at the start of the process")
