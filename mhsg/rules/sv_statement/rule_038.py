# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules import sv_types
from mhsg.rules.sv_tree import TreeRule

SIGNALS = ("NamedValue", "ElementSelect", "RangeSelect", "MemberAccess", "Concatenation")


class rule_038(TreeRule, structure.Rule):
    """
    This rule checks that the value of an assignment, a signal, a part of one or a concatenation, is not narrower
    than its target, as the STARC guide recommends (2.10.3.4): extend it explicitly; sv_statement_039 checks the
    results of additions and multiplications. Constants, such as numbers, parameters and strings, and fills such as
    '0, are not checked; values wider than their target are slang's WidthTruncate warning, sv_lint_001. The widths
    come from slang's elaboration of the file. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       assign sum = a;  // 9 and 8 bits

    **Fix**

    .. code-block:: systemverilog

       assign sum = {1'b0, a};
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        lFound = []
        for oNode in sv_types.nodes(oFile, "Assignment"):
            if sv_types.unsized(oNode.right) or sv_types.constant(oNode.right) or sv_types.own(oNode.right).kind.name not in SIGNALS:
                continue
            iLeft, iRight = sv_types.width(oNode.left), sv_types.width(oNode.right)
            if iLeft is not None and iRight is not None and iRight < iLeft:
                lFound.append((oNode, f"Extend {sv_types.text(oNode.right)}, {iRight} bits wide, to the {iLeft} bits of {sv_types.text(oNode.left)}"))
        return sv_types.problems(oFile, lFound)
