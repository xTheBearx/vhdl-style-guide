# -*- coding: utf-8 -*-

from mhsg.rules.sv_spacing import Rule, kind, node


class rule_012(Rule):
    """
    This rule checks for no space between a name and the bracket of a select, such as data[0]; the packed
    dimensions of a type, as in data_t [1:0], keep their space, as Verible's formatter does.

    **Violation**

    .. code-block:: systemverilog

       assign first = data [0];

    **Fix**

    .. code-block:: systemverilog

       assign first = data[0];
    """

    def __init__(self):
        super().__init__()
        self.solution = "Remove space before ["

    def spacing(self, oLeft, oRight):
        if kind(oRight) == "OpenBracket" and node(oRight) == "ElementSelect" and node(oRight, 3) != "NamedType":
            return (0, True)
        return None
