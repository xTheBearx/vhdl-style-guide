# -*- coding: utf-8 -*-

from mhsg.rules.sv_spacing import Rule, kind


class rule_003(Rule):
    """
    This rule checks for no space before a semicolon, except one after the colon of an empty case item (default:
    ;), as Verible's formatter does.

    **Violation**

    .. code-block:: systemverilog

       assign a = b ;

    **Fix**

    .. code-block:: systemverilog

       assign a = b;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Remove space before semicolon"

    def spacing(self, oLeft, oRight):
        if kind(oRight) == "Semicolon":
            return (1, True) if kind(oLeft) == "Colon" else (0, True)
        return None
