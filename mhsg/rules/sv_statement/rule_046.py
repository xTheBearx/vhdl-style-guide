# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules import sv_types
from mhsg.rules.sv_tree import TreeRule


class rule_046(TreeRule, structure.Rule):
    """
    This rule checks for operations that mix signed and unsigned operands, as the STARC guide asks (2.10.6.3):
    Verilog and SystemVerilog then treat both as unsigned. The types come from slang's elaboration of the file;
    numbers without a width are not checked. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       logic signed [7:0] s;
       assign y = s + u;

    **Fix**

    .. code-block:: systemverilog

       assign y = s + signed'(u);
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        lFound = []
        for oNode in sv_types.nodes(oFile, "BinaryOp"):
            if sv_types.unsized(oNode.left) or sv_types.unsized(oNode.right):
                continue
            lSigned = [getattr(getattr(sv_types.own(o), "type", None), "isSigned", None) for o in (oNode.left, oNode.right)]
            if None not in lSigned and lSigned[0] != lSigned[1]:
                lFound.append((oNode, f"Do not mix signed and unsigned operands in {sv_types.text(oNode)}"))
        return sv_types.problems(oFile, lFound)
