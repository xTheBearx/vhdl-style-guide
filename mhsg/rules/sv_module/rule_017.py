# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import inside, text
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_017(TreeRule, structure.Rule):
    """
    This rule checks that the outputs of a module are registered, not driven by logic of a continuous assignment or a
    combinational always block, as the STARC guide recommends (1.6.2.1) for basic blocks. An output assigned a signal
    as it is, such as assign y_o = q, is taken to be registered. It is disabled by default; the starc rule set
    enables it.

    **Violation**

    .. code-block:: systemverilog

       assign y_o = a & b;

    **Fix**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i) y_o <= a & b;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        setOutputs = set()
        for oPort in oFile.nodes("ImplicitAnsiPort"):
            if oPort.header is not None and text(getattr(oPort.header, "direction", None)) == "output" and oPort.declarator is not None:
                setOutputs.add(text(oPort.declarator.name))
        setDone = set()
        for oNode in oFile.nodes("AssignmentExpression", "NonblockingAssignmentExpression"):
            if oNode.left is None or oNode.right is None:
                continue
            sName = text(oNode.left.getFirstToken())
            if sName not in setOutputs or sName in setDone:
                continue
            bAssign = inside(oNode, "ContinuousAssign") and oNode.right.kind.name not in ("IdentifierName", "IdentifierSelectName")
            if bAssign or inside(oNode, "AlwaysCombBlock"):
                setDone.add(sName)
                oToken = oFile.token_at(oNode.left.getFirstToken())
                if oToken is not None:
                    yield Problem(oToken, f"Register the output {sName}")
