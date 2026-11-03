# -*- coding: utf-8 -*-

from mhsg.rules.sv_spacing import Rule, kind, node


class rule_013(Rule):
    """
    This rule checks for one space on each side of the colon of a block label, such as begin : name and end :
    name, as Verible's formatter does.

    **Violation**

    .. code-block:: systemverilog

       end: gen_stage

    **Fix**

    .. code-block:: systemverilog

       end : gen_stage
    """

    def __init__(self):
        super().__init__()
        self.solution = "Use one space around the colon of the label"

    def spacing(self, oLeft, oRight):
        if kind(oRight) == "Colon" and node(oRight) == "NamedBlockClause":
            return (1, True)
        if kind(oLeft) == "Colon" and node(oLeft) == "NamedBlockClause":
            return (1, True)
        return None
