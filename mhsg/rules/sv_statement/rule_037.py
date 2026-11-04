# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules import sv_types
from mhsg.rules.sv_tree import TreeRule


class rule_037(TreeRule, structure.Rule):
    """
    This rule checks that the operands of comparisons have the same width, as the STARC guide asks (2.10.3.1).
    Constants, such as numbers, parameters and Width - 1, expressions with a number without a width, strings and
    integers, which sv_statement_043 checks, are not checked here. The widths come from slang's elaboration of the
    file. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       if (count == limit) ...  // 8 and 6 bits

    **Fix**

    .. code-block:: systemverilog

       if (count == {2'b00, limit}) ...
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        lFound = []
        for oNode in sv_types.nodes(oFile, "BinaryOp"):
            if (
                sv_types.operator(oNode)
                not in ("Equality", "Inequality", "CaseEquality", "CaseInequality", "LessThan", "LessThanEqual", "GreaterThan", "GreaterThanEqual")
                or sv_types.constant(oNode.left)
                or sv_types.constant(oNode.right)
            ):
                continue
            if any(str(getattr(sv_types.own(o), "type", "")) in ("int", "integer") for o in (oNode.left, oNode.right)):
                # sv_statement_043 checks integers
                continue
            if sv_types.has_unsized(oNode.left) or sv_types.has_unsized(oNode.right):
                continue
            iLeft, iRight = sv_types.width(oNode.left), sv_types.width(oNode.right)
            if iLeft and iRight and iLeft != iRight:
                lFound.append(
                    (oNode, f"Compare operands of the same width: {sv_types.text(oNode.left)} has {iLeft} bits, {sv_types.text(oNode.right)} {iRight}"),
                )
        return sv_types.problems(oFile, lFound)
