# -*- coding: utf-8 -*-

from mhsg.rules.sv_spacing import ALWAYS_KEYWORDS, Rule, kind


class rule_006(Rule):
    """
    This rule checks for no space between @ and its parenthesis or :code:`*`, and one space between an always keyword
    and @, as Verible's formatter does.

    **Violation**

    .. code-block:: systemverilog

       always_ff@ (posedge clk_i) begin

    **Fix**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i) begin
    """

    def __init__(self):
        super().__init__()
        self.solution = "Use @( after one space"

    def spacing(self, oLeft, oRight):
        if kind(oLeft) == "At" and kind(oRight) in ("OpenParenthesis", "Star"):
            return (0, True)
        if kind(oLeft) in ALWAYS_KEYWORDS and kind(oRight) == "At":
            return (1, True)
        return None
