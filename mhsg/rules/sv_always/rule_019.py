# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_always.rule_012 import clock_events
from mhsg.rules.sv_nodes import integer_of, source, text
from mhsg.rules.sv_tree import Problem, TreeRule, descendants

ASSIGNMENTS = ("NonblockingAssignmentExpression", "AssignmentExpression")


class rule_019(TreeRule, structure.Rule):
    """
    This rule checks for registers that an edge triggered always block only ever assigns one constant, so their data
    input is constant, as the STARC guide recommends (2.3.5.1, 3.3.3.2). A part of a signal, such as q[0], is not
    reported if the block also assigns other values to the signal, nor are the registers of blocks that call tasks,
    which may assign them too. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i or negedge rst_ni)
           if (!rst_ni) ready <= 1'b1;
           else ready <= 1'b1;

    **Fix**

    .. code-block:: systemverilog

       assign ready = 1'b1;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oBlock in oFile.nodes("AlwaysBlock", "AlwaysFFBlock"):
            lClocks, _ = clock_events(oBlock)
            if not lClocks or calls_task(oBlock):
                continue
            dValues = {}
            dFirst = {}
            setVariable = set()
            for oNode in descendants(oBlock):
                if oNode.kind.name not in ASSIGNMENTS or oNode.left is None or oNode.parent.kind.name == "ForLoopStatement":
                    continue
                sTarget = "".join(source(oNode.left).split())
                dFirst.setdefault(sTarget, oNode.left.getFirstToken())
                iValue = integer_of(oNode.right) if oNode.right is not None else None
                if iValue is None and oNode.right is not None and oNode.right.kind.name == "UnbasedUnsizedLiteralExpression":
                    iValue = text(oNode.right.literal)
                dValues.setdefault(sTarget, set()).add(iValue)
                if iValue is None:
                    setVariable.add(text(oNode.left.getFirstToken()))
            for sTarget, setValues in dValues.items():
                if len(setValues) == 1 and None not in setValues and text(dFirst[sTarget]) not in setVariable:
                    oToken = oFile.token_at(dFirst[sTarget])
                    if oToken is not None:
                        yield Problem(oToken, f"The register {sTarget} is always assigned the same constant: use the constant")


def calls_task(oBlock):
    """True if a block has a statement that calls a task, such as send(data); or send;."""
    for oNode in descendants(oBlock):
        if oNode.kind.name == "ExpressionStatement" and oNode.expr is not None:
            oCall = oNode.expr
            if oCall.kind.name == "IdentifierName" or (oCall.kind.name == "InvocationExpression" and oCall.left.kind.name != "SystemName"):
                return True
    return False
