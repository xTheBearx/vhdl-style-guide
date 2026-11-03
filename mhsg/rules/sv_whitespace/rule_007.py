# -*- coding: utf-8 -*-

from mhsg.rules.sv_spacing import Rule, kind


class rule_007(Rule):
    """
    This rule checks for no space after # in parameter lists and delays, as Verible's formatter does.

    **Violation**

    .. code-block:: systemverilog

       fifo # (.Depth(4)) u_fifo (

    **Fix**

    .. code-block:: systemverilog

       fifo #(.Depth(4)) u_fifo (
    """

    def __init__(self):
        super().__init__()
        self.solution = "Remove space after #"

    def spacing(self, oLeft, oRight):
        if kind(oLeft) == "Hash":
            return (0, True)
        return None
