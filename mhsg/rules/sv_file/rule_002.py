# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import file_stem, text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_002(TreeRule, structure.Rule):
    """
    This rule checks a file holding a package is named after it, as Verible's package-filename rule does:
    fifo_pkg.sv holds package fifo_pkg.

    **Violation**

    .. code-block:: systemverilog

       // file types.sv
       package fifo_pkg;

    **Fix**

    .. code-block:: systemverilog

       // file fifo_pkg.sv
       package fifo_pkg;
    """

    def __init__(self):
        super().__init__()
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        if not oFile.filename:
            return
        sStem = file_stem(oFile.filename)
        for oPackage in oFile.nodes("PackageDeclaration"):
            if text(oPackage.header.name) != sStem:
                oToken = oFile.token_at(oPackage.header.name)
                if oToken is not None:
                    yield Problem(oToken, f"Name the file after package {text(oPackage.header.name)}")
