# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import anonymous_types
from mhsg.rules.sv_tree import TreeRule


class rule_002(TreeRule, structure.Rule):
    """
    This rule checks that struct and union types are declared with typedef, not anonymously in a declaration, as
    Verible's typedef-structs-unions rule does.

    **Violation**

    .. code-block:: systemverilog

       struct packed {logic a;} beat;

    **Fix**

    .. code-block:: systemverilog

       typedef struct packed {logic a;} beat_t;
       beat_t beat;
    """

    def __init__(self):
        super().__init__()
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        yield from anonymous_types(oFile, ("StructType", "UnionType"), "Declare the struct or union type with typedef")
