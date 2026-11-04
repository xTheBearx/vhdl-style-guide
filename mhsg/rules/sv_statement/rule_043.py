# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules import sv_types
from mhsg.rules.sv_tree import TreeRule


class rule_043(TreeRule, structure.Rule):
    """
    This rule checks for comparisons of an integer, such as an int or integer variable, with a vector of another
    type, as the STARC guide recommends (2.10.4.4): their widths and signs differ. The widths come from slang's
    elaboration of the file. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       integer i;
       if (i == count) ...

    **Fix**

    .. code-block:: systemverilog

       if (i == int'(count)) ...
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        lFound = []
        for oNode in sv_types.nodes(oFile, "BinaryOp"):
            if sv_types.operator(oNode) not in (
                "Equality",
                "Inequality",
                "CaseEquality",
                "CaseInequality",
                "LessThan",
                "LessThanEqual",
                "GreaterThan",
                "GreaterThanEqual",
            ):
                continue
            lTypes = [str(getattr(sv_types.own(o), "type", "")) for o in (oNode.left, oNode.right)]
            lInteger = [s in ("int", "integer") for s in lTypes]
            if any(lInteger) and not all(lInteger) and not sv_types.unsized(oNode.left) and not sv_types.unsized(oNode.right):
                lFound.append((oNode, f"Compare values of one type: {sv_types.text(oNode)} compares {lTypes[0]} with {lTypes[1]}"))
        return sv_types.problems(oFile, lFound)
