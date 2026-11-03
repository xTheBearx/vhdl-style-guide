# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import anonymous_types
from mhsg.rules.sv_tree import TreeRule


class rule_001(TreeRule, structure.Rule):
    """
    This rule checks that enum types are declared with typedef, not anonymously in a declaration, as Verible's
    typedef-enums rule does.

    **Violation**

    .. code-block:: systemverilog

       enum logic {Idle, Busy} state;

    **Fix**

    .. code-block:: systemverilog

       typedef enum logic {Idle, Busy} state_e;
       state_e state;
    """

    def __init__(self):
        super().__init__()
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        yield from anonymous_types(oFile, ("EnumType",), "Declare the enum type with typedef")
