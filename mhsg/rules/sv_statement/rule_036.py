# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules import sv_types
from mhsg.rules.sv_tree import TreeRule


class rule_036(TreeRule, structure.Rule):
    """
    This rule checks that the conditions of if statements and conditional operators are 1 bit wide, as the STARC
    guide asks (2.1.5.3). Calls of functions, such as $test$plusargs, are not checked. The widths come from slang's
    elaboration of the file. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       if (count) ...

    **Fix**

    .. code-block:: systemverilog

       if (count != '0) ...
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        lFound = []
        for oNode in sv_types.nodes(oFile, "Conditional", "ConditionalOp"):
            for oCondition in oNode.conditions:
                iWidth = sv_types.width(oCondition.expr)
                if iWidth is not None and iWidth > 1 and not sv_types.unsized(oCondition.expr) and not sv_types.call(oCondition.expr):
                    lFound.append((oCondition.expr, f"Make the condition {sv_types.text(oCondition.expr)} 1 bit wide: it has {iWidth} bits"))
        return sv_types.problems(oFile, lFound)
