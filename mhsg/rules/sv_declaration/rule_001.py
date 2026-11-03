# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, elements


class rule_001(TreeRule, structure.Rule):
    """
    This rule checks that parameters and localparams are declared with a type, such as int or logic [7:0], as
    Verible's explicit-parameter-storage-type rule does.

    **Violation**

    .. code-block:: systemverilog

       parameter Depth = 8;

    **Fix**

    .. code-block:: systemverilog

       parameter int Depth = 8;
    """

    def __init__(self):
        super().__init__()
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes("ParameterDeclaration"):
            if oNode.type is not None and oNode.type.kind.name == "ImplicitType":
                for oDeclarator in elements(oNode.declarators):
                    oToken = oFile.token_at(oDeclarator.name)
                    if oToken is not None:
                        yield Problem(oToken, f"Give {text(oDeclarator.name)} a type")
