# -*- coding: utf-8 -*-

from mhsg import parser
from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_004(TreeRule, structure.Rule):
    """
    This rule checks for generate regions: the generate and endgenerate keywords are not needed.

    **Violation**

    .. code-block:: systemverilog

       generate
           for (genvar i = 0; i < Depth; i++) begin : gen_stage
               assign stage[i] = data_i;
           end
       endgenerate

    **Fix**

    .. code-block:: systemverilog

       for (genvar i = 0; i < Depth; i++) begin : gen_stage
           assign stage[i] = data_i;
       end
    """

    def __init__(self):
        super().__init__()
        self.fixable = True
        self.solution = "Remove generate and endgenerate"

    def problems(self, oFile):
        for oRegion in oFile.nodes("GenerateRegion"):
            oFirst = oFile.token_at(oRegion.keyword)
            oLast = oFile.token_at(oRegion.endgenerate)
            if oFirst is not None and oLast is not None:
                yield Problem(oFirst, self.solution, oLast)

    def _fix_violation(self, oViolation):
        lTokens = list(oViolation.get_tokens())
        # generate, and its line end when it is alone on its line
        del lTokens[0]
        while lTokens and isinstance(lTokens[0], parser.whitespace):
            del lTokens[0]
        if lTokens and isinstance(lTokens[0], parser.carriage_return):
            del lTokens[0]
        # endgenerate, and the line end and indent before it when it is alone on its line
        del lTokens[-1]
        while lTokens and isinstance(lTokens[-1], parser.whitespace):
            del lTokens[-1]
        if lTokens and isinstance(lTokens[-1], parser.carriage_return):
            del lTokens[-1]
        oViolation.set_tokens(lTokens)
