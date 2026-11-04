# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, elements

LITERALS = ("IntegerLiteralExpression", "IntegerVectorExpression", "UnbasedUnsizedLiteralExpression")


class rule_004(TreeRule, structure.Rule):
    """
    This rule checks that output ports are not driven by a constant in a continuous assignment, as the STARC guide
    asks (1.1.4.6). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       assign ready_o = 1'b1;

    **Fix**

    Drive the output from a register or logic, or remove the port.
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
        for oAssign in oFile.nodes("ContinuousAssign"):
            for oAssignment in elements(oAssign.assignments):
                if oAssignment.kind.name != "AssignmentExpression" or oAssignment.right is None or oAssignment.right.kind.name not in LITERALS:
                    continue
                oFirst = oAssignment.left.getFirstToken()
                if text(oFirst) in setOutputs:
                    oToken = oFile.token_at(oFirst)
                    if oToken is not None:
                        yield Problem(oToken, f"Do not drive the output {text(oFirst)} with a constant")
