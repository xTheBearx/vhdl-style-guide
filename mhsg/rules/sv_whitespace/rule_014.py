# -*- coding: utf-8 -*-

from mhsg import parser
from mhsg.rules.sv_spacing import CASE_ITEMS, Rule, kind, node


class rule_014(Rule):
    """
    This rule checks for no space before the colon of a case item and at least one after it, as Verible's
    formatter does.

    **Violation**

    .. code-block:: systemverilog

       Idle : state_d = Busy;

    **Fix**

    .. code-block:: systemverilog

       Idle: state_d = Busy;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Remove space before the colon of the case item"

    def spacing(self, oLeft, oRight):
        if kind(oRight) == "Colon" and node(oRight) in CASE_ITEMS:
            return (0, True)
        if kind(oLeft) == "Colon" and node(oLeft) in CASE_ITEMS and not isinstance(oRight, parser.comment):
            return (1, False)
        return None
