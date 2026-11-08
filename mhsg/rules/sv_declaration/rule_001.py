# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import is_verilog, text
from mhsg.rules.sv_tree import Problem, TreeRule, elements


class rule_001(TreeRule, structure.Rule):
    """
    This rule checks that parameters and localparams are declared with a type, such as int or logic [7:0], as
    Verible's explicit-parameter-storage-type rule does. In a Verilog file, which can give a parameter only the types
    integer, real, realtime and time, a range or signed is taken as its type, as in parameter [7:0] Mask.

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
        bVerilog = is_verilog(oFile)
        for oNode in oFile.nodes("ParameterDeclaration"):
            if oNode.type is None or oNode.type.kind.name != "ImplicitType":
                continue
            if bVerilog and (text(oNode.type.signing) or elements(oNode.type.dimensions)):
                continue
            for oDeclarator in elements(oNode.declarators):
                oToken = oFile.token_at(oDeclarator.name)
                if oToken is not None:
                    sName = text(oDeclarator.name)
                    yield Problem(oToken, f"Give {sName} a type, such as integer, or a range" if bVerilog else f"Give {sName} a type")
