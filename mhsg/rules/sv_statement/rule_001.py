# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule

# Statements whose body must be a begin-end block, with the field holding the body
CONTROLS = {
    "ConditionalStatement": "statement",
    "ElseClause": "clause",
    "ForLoopStatement": "statement",
    "ForeachLoopStatement": "statement",
    "LoopStatement": "statement",
    "ForeverStatement": "statement",
    "AlwaysBlock": "statement",
    "AlwaysFFBlock": "statement",
    "AlwaysCombBlock": "statement",
    "AlwaysLatchBlock": "statement",
    "InitialBlock": "statement",
    "FinalBlock": "statement",
}
BLOCKS = ("SequentialBlockStatement", "ParallelBlockStatement")


class rule_001(TreeRule, structure.Rule):
    """
    This rule checks that the statement of an if, else, for, foreach, while, repeat, forever, always or initial
    is a begin-end block, as Verible's explicit-begin rule does. An else if needs no block of its own.

    **Violation**

    .. code-block:: systemverilog

       if (valid_i)
           data_d = data_i;

    **Fix**

    .. code-block:: systemverilog

       if (valid_i) begin
           data_d = data_i;
       end
    """

    def __init__(self):
        super().__init__()
        self.solution = "Use a begin-end block"

    def problems(self, oFile):
        for sKind, sField in CONTROLS.items():
            for oNode in oFile.nodes(sKind):
                if oNode.kind.name == "ElseClause" and oNode.parent is not None and oNode.parent.kind.name != "ConditionalStatement":
                    # The else of a generate if is checked by the generate rules
                    continue
                oStatement = getattr(oNode, sField, None)
                if oStatement is None:
                    continue
                if oStatement.kind.name == "TimingControlStatement":
                    oStatement = oStatement.statement
                    if oStatement is None:
                        continue
                if oStatement.kind.name in BLOCKS:
                    continue
                if sKind == "ElseClause" and oStatement.kind.name == "ConditionalStatement":
                    continue
                oToken = oFile.token_at(oNode.getFirstToken())
                if oToken is not None:
                    yield Problem(oToken, self.solution)
