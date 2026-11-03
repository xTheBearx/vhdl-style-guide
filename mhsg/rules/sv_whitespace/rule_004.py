# -*- coding: utf-8 -*-

from mhsg import parser
from mhsg.rules.sv_spacing import Rule, kind


class rule_004(Rule):
    """
    This rule checks for at least one space after a semicolon followed by more code on the line, as in a for
    loop, as Verible's formatter does.

    **Violation**

    .. code-block:: systemverilog

       for (int i = 0;i < 4;i++) begin

    **Fix**

    .. code-block:: systemverilog

       for (int i = 0; i < 4; i++) begin
    """

    def __init__(self):
        super().__init__()
        self.solution = "Add a space after semicolon"

    def spacing(self, oLeft, oRight):
        if kind(oLeft) == "Semicolon" and kind(oRight) not in ("Semicolon", "CloseParenthesis") and not isinstance(oRight, parser.comment):
            return (1, False)
        return None
