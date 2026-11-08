# -*- coding: utf-8 -*-

from mhsg import language
from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule

# Blocks, with the fields of their begin label, prefix label and end label
BLOCKS = {
    "SequentialBlockStatement": ("blockName", "label", "endBlockName"),
    "ParallelBlockStatement": ("blockName", "label", "endBlockName"),
    "GenerateBlock": ("beginName", "label", "endName"),
}


class rule_001(TreeRule, structure.Rule):
    """
    This rule checks that the label after end matches the label of its begin. An end label without a begin label is
    removed.

    **Violation**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i) begin : proc_count
       end : proc_counter

    **Fix**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i) begin : proc_count
       end : proc_count
    """

    def __init__(self):
        super().__init__()
        # SystemVerilog only: it checks end labels, which Verilog-2005 does not have
        self.languages = (language.SYSTEMVERILOG,)
        self.fixable = True
        self.solution = "Make the end label match the begin label"

    def problems(self, oFile):
        for sKind, (sBegin, sPrefix, sEnd) in BLOCKS.items():
            for oBlock in oFile.nodes(sKind):
                oEnd = getattr(oBlock, sEnd, None)
                if oEnd is None:
                    continue
                oBegin = getattr(oBlock, sBegin, None) or getattr(oBlock, sPrefix, None)
                if oBegin is None:
                    oFirst = oFile.token_at(oBlock.end)
                    oLast = oFile.token_at(oEnd.name)
                    if oFirst is not None and oLast is not None:
                        yield Problem(oFirst, "Remove the end label, the block has no begin label", oLast, {"remove": True})
                elif oBegin.name.rawText != oEnd.name.rawText:
                    oToken = oFile.token_at(oEnd.name)
                    if oToken is not None:
                        yield Problem(oToken, f"Change the end label to {oBegin.name.rawText}", dAction={"name": oBegin.name.rawText})

    def _fix_violation(self, oViolation):
        dAction = oViolation.get_action()
        lTokens = oViolation.get_tokens()
        if dAction.get("remove"):
            oViolation.set_tokens([lTokens[0]])
        else:
            lTokens[0].set_value(dAction["name"])
