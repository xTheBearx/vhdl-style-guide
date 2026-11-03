# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule


class rule_005(Rule):
    """
    This rule checks that every case statement has a :code:`when others` choice.

    .. NOTE:: This is a lint rule. It runs in lint mode and implements DO-254 check SS2.

    Without :code:`when others`, the behaviour for values that are not listed, such as an illegal state after a single event upset, depends on the synthesis tool.
    This includes case statements whose choices list every value of an enumerated type.

    **Violation**

    .. code-block:: vhdl

       case addr is
         when "00" => sel <= '1';
         when "01" => sel <= '0';
       end case;

    **Fix**

    .. code-block:: vhdl

       case addr is
         when "00" => sel <= '1';
         when "01" => sel <= '0';
         when others => sel <= '0';
       end case;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Add a when others choice"

    def check(self, oModel, oFile):
        for oCase in cases(oModel):
            if not any(o.others for o in oCase.alternatives):
                self.report(oFile, oCase.index, "Add a when others choice to the case statement")


def cases(oModel):
    """Yields every case statement in the processes of the file."""
    for oArchitecture in oModel.architectures:
        for oProcess in oArchitecture.processes:
            for oStatement in model.walk(oProcess.statements):
                if isinstance(oStatement, model.Case):
                    yield oStatement
