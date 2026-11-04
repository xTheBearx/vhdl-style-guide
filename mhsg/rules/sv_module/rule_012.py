# -*- coding: utf-8 -*-

import fnmatch
from functools import lru_cache

import yaml

from mhsg.design import black_box
from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_012(TreeRule, structure.Rule):
    """
    This rule checks for instances of vendor primitives, the types of the black box libraries that come with mhsg,
    such as BUFG or RAMB36E1, as the STARC guide recommends (3.1.2.2): keep technology dependent code apart. It is
    disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       BUFG u_bufg (.I(clk_in), .O(clk));

    **Fix**

    Instantiate the primitive in a technology dependent module, or let synthesis infer it.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        lTypes = vendor_types()
        for oNode in oFile.nodes("HierarchyInstantiation"):
            sType = text(oNode.type)
            if any(fnmatch.fnmatchcase(sType.lower(), s) for s in lTypes):
                oToken = oFile.token_at(oNode.type)
                if oToken is not None:
                    yield Problem(oToken, f"Keep the vendor primitive {sType} out of the technology independent code")


@lru_cache(maxsize=1)
def vendor_types():
    """The names and patterns of the types of the black box libraries that come with mhsg, in lower case."""
    lReturn = []
    for sLibrary in black_box.built_in_libraries():
        with open(black_box.library_file(sLibrary), encoding="utf-8") as oFile:
            lReturn += [str(s).lower() for s in (yaml.safe_load(oFile).get("black_boxes") or {})]
    return tuple(lReturn)
