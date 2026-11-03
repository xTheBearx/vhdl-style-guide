# -*- coding: utf-8 -*-

from mhsg.rules.sv_spacing import Rule, is_unary_operator


class rule_009(Rule):
    """
    This rule checks for no space between a unary operator and its operand, as Verible's formatter does.

    **Violation**

    .. code-block:: systemverilog

       assign ready = ~ busy;

    **Fix**

    .. code-block:: systemverilog

       assign ready = ~busy;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Remove space after unary operator"

    def spacing(self, oLeft, oRight):
        if is_unary_operator(oLeft):
            return (0, True)
        return None
