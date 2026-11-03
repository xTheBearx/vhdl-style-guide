# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import file_stem, text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_001(TreeRule, structure.Rule):
    """
    This rule checks a file holding modules is named after one of them, as Verible's module-filename rule does:
    counter.sv holds module counter.

    **Violation**

    .. code-block:: systemverilog

       // file fifo_top.sv
       module fifo;

    **Fix**

    .. code-block:: systemverilog

       // file fifo.sv
       module fifo;
    """

    def __init__(self):
        super().__init__()
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        lModules = oFile.nodes("ModuleDeclaration")
        if not lModules or not oFile.filename:
            return
        sStem = file_stem(oFile.filename)
        if any(text(o.header.name) == sStem for o in lModules):
            return
        oToken = oFile.token_at(lModules[-1].header.name)
        if oToken is not None:
            yield Problem(oToken, f"Name the file after module {text(lModules[-1].header.name)}")
