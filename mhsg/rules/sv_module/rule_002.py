# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_002(TreeRule, structure.Rule):
    """
    This rule checks for defparam statements; set parameters in the instantiation instead.

    |unfixable|

    **Violation**

    .. code-block:: systemverilog

       fifo u_fifo (.clk_i);
       defparam u_fifo.Depth = 8;

    **Fix**

    .. code-block:: systemverilog

       fifo #(.Depth(8)) u_fifo (.clk_i);
    """

    def __init__(self):
        super().__init__()
        self.solution = "Set the parameter in the instantiation instead of with defparam"

    def problems(self, oFile):
        for oNode in oFile.nodes("DefParam"):
            oToken = oFile.token_at(oNode.defparam)
            if oToken is not None:
                yield Problem(oToken, self.solution)
