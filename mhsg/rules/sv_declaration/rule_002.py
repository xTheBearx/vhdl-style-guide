# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, elements


class rule_002(TreeRule, structure.Rule):
    """
    This rule checks that every parameter has a default value, as the STARC guide asks (3.1.5.3). It is disabled by
    default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       module fifo #(parameter int Depth) ();

    **Fix**

    .. code-block:: systemverilog

       module fifo #(parameter int Depth = 4) ();
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("ParameterDeclaration"):
            for oDeclarator in elements(oNode.declarators):
                if oDeclarator.initializer is None:
                    oToken = oFile.token_at(oDeclarator.name)
                    if oToken is not None:
                        yield Problem(oToken, f"Give {text(oDeclarator.name)} a default value")
