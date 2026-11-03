# -*- coding: utf-8 -*-

from mhsg.rules.sv_spacing import CONTROL_KEYWORDS, Rule, kind


class rule_005(Rule):
    """
    This rule checks for one space between if, for, foreach, while, repeat, wait or case and its opening
    parenthesis, as Verible's formatter does.

    **Violation**

    .. code-block:: systemverilog

       if(valid) begin

    **Fix**

    .. code-block:: systemverilog

       if (valid) begin
    """

    def __init__(self):
        super().__init__()
        self.solution = "Use one space between the keyword and ("

    def spacing(self, oLeft, oRight):
        if kind(oLeft) in CONTROL_KEYWORDS and kind(oRight) == "OpenParenthesis":
            return (1, True)
        return None
