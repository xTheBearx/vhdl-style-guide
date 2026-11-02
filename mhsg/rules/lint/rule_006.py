# -*- coding: utf-8 -*-

from mhsg.lint.rule import Rule
from mhsg.rules.lint.rule_005 import cases


class rule_006(Rule):
    """
    This rule checks that no choice appears twice in a case statement.

    .. NOTE:: This is a lint rule. It runs in lint mode and implements DO-254 check SS2.

    Choices are compared as written, ignoring case and spaces.
    Overlapping ranges are not detected.

    **Violation**

    .. code-block:: vhdl

       case addr is
         when "000" => clk_div_en <= '1';
         when "001" => clk_div_en <= '1';
         when "000" => clk_div_en <= '0';
         when others => clk_div_en <= '0';
       end case;

    **Fix**

    .. code-block:: vhdl

       case addr is
         when "000" => clk_div_en <= '1';
         when "001" => clk_div_en <= '1';
         when others => clk_div_en <= '0';
       end case;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Remove the duplicate choice"

    def check(self, oModel, oFile):
        for oCase in cases(oModel):
            dFirst = {}
            for oAlternative in oCase.alternatives:
                for sChoice, sText, iIndex in zip(oAlternative.choices, oAlternative.choice_texts, oAlternative.choice_indexes):
                    if sChoice in dFirst:
                        self.report(oFile, iIndex, f"Choice {sText} is already covered on line {dFirst[sChoice]}")
                    else:
                        dFirst[sChoice] = oAlternative.line
