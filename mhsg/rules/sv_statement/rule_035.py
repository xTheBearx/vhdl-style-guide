# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules import sv_types
from mhsg.rules.sv_tree import TreeRule


class rule_035(TreeRule, structure.Rule):
    """
    This rule checks that the operands of the logical operators &&, || and ! are 1 bit wide, as the STARC guide asks
    (2.1.4.5): compare a vector with a value instead. The widths come from slang's elaboration of the file. It is
    disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       if (count && valid) ...

    **Fix**

    .. code-block:: systemverilog

       if ((count != '0) && valid) ...
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        lFound = []
        for oNode in sv_types.nodes(oFile, "BinaryOp", "UnaryOp"):
            if sv_types.operator(oNode) not in ("LogicalAnd", "LogicalOr", "LogicalNot"):
                continue
            for oOperand in (oNode.left, oNode.right) if oNode.kind.name == "BinaryOp" else (oNode.operand,):
                iWidth = sv_types.width(oOperand)
                if iWidth is not None and iWidth > 1 and not sv_types.unsized(oOperand) and not sv_types.call(oOperand):
                    lFound.append((oOperand, f"Compare {sv_types.text(oOperand)}, {iWidth} bits wide, with a value instead of using it as a truth value"))
        return sv_types.problems(oFile, lFound)
