# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule, signal_kind


class rule_009(Rule):
    """
    This rule checks for latches: signals that a combinational process assigns on some paths but not on all of them.

    .. NOTE:: This is a lint rule. It runs in lint mode and implements DO-254 check SS4.

    A signal keeps its value on the paths that do not assign it, so synthesis infers a latch.
    Assign a default value at the start of the process, or assign the signal in every branch.
    An assignment to part of a signal, such as :code:`out2(3)`, does not count as assigning the whole signal.
    An if statement whose condition reads no signal, such as :code:`if IMPLEMENT_WRITE_G then`, is decided at elaboration and is not a latch.

    **Violation**

    .. code-block:: vhdl

       process (in1, in2, in3, in4) is
       begin
         if in4 = '0' then
           out1 <= in1;
         end if;
       end process;

    **Fix**

    .. code-block:: vhdl

       process (in1, in2, in3, in4) is
       begin
         if in4 = '0' then
           out1 <= in1;
         else
           out1 <= in2;
         end if;
       end process;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Assign the signal on every path"

    def check(self, oModel, oFile):
        for oArchitecture in oModel.architectures:
            for oProcess in oArchitecture.processes:
                if not model.is_combinational(oProcess):
                    continue
                def fStatic(lCondition, oArchitecture=oArchitecture, oProcess=oProcess):
                    # Only names known to be constants or generics make a condition static
                    return all(signal_kind(oFile, oArchitecture, s, oProcess.index) == "other" for s in model.names(lCondition))

                setDefinite = model.definitely_assigned(oProcess.statements, fStatic)
                lReported = []
                for oAssignment in model.assignments(oProcess.statements):
                    sPart = oAssignment.covers()
                    if model.covered(sPart, setDefinite) or sPart in lReported:
                        continue
                    lReported.append(sPart)
                    self.report(oFile, oAssignment.index, f"Signal {sPart} is not assigned on every path of the combinational process, which infers a latch")
