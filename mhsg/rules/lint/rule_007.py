# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule
from mhsg.rules.lint.rule_005 import cases


class rule_007(Rule):
    """
    This rule checks for case choices that can never be reached in hardware.

    .. NOTE:: This is a lint rule. It runs in lint mode and implements DO-254 check SS2.

    A string or character choice containing a metavalue, such as X, Z, U, W or -, never matches a real signal value.
    In a matching case statement, :code:`case?`, the - is a don't care and is allowed.

    **Violation**

    .. code-block:: vhdl

       case addr is
         when "000" => sel <= '1';
         when "10X" => sel <= '0';
         when others => sel <= '0';
       end case;

    **Fix**

    .. code-block:: vhdl

       case addr is
         when "000" => sel <= '1';
         when others => sel <= '0';
       end case;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Remove the unreachable choice"

    def check(self, oModel, oFile):
        for oCase in cases(oModel):
            for oAlternative in oCase.alternatives:
                for sChoice, iIndex in zip(oAlternative.choice_texts, oAlternative.choice_indexes):
                    sTest = sChoice.lower().replace("-", "") if oCase.matching else sChoice.lower()
                    if model.is_metavalue_choice(sTest):
                        self.report(oFile, iIndex, f"Choice {sChoice} contains a metavalue and is never reached in hardware")
