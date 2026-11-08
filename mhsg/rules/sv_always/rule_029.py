# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule

ALWAYS = ("AlwaysBlock", "AlwaysFFBlock", "AlwaysCombBlock", "AlwaysLatchBlock")


class rule_029(TreeRule, structure.Rule):
    """
    This rule checks that always blocks are labelled: their statement is a begin-end block with a name, such as
    begin : p_count, so that reports, waveforms and reviews can name the block. It is disabled by default; the do254
    rule set enables it (DR1), with sv_generate_001 for the blocks of generate constructs.

    **Violation**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i) begin
           count <= count + 1;
       end

    **Fix**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i) begin : p_count
           count <= count + 1;
       end
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "Label the always block, with begin : name"

    def problems(self, oFile):
        for oBlock in oFile.nodes(*ALWAYS):
            oStatement = oBlock.statement
            # The statement after the event control of an always or always_ff block
            if oStatement is not None and oStatement.kind.name == "TimingControlStatement":
                oStatement = oStatement.statement
            if oStatement is not None and oStatement.kind.name == "SequentialBlockStatement":
                if oStatement.blockName is not None or oStatement.label is not None:
                    continue
            oToken = oFile.token_at(oBlock.keyword)
            if oToken is not None:
                yield Problem(oToken, self.solution)
