# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import text
from mhsg.rules.sv_tree import Problem, TreeRule, elements

INVERSIONS = ("UnaryBitwiseNotExpression", "UnaryLogicalNotExpression")
NAMES = ("IdentifierName",)


class rule_051(TreeRule, structure.Rule):
    """
    This rule checks for chains of inverters: a continuous assignment that only inverts a signal that another such
    assignment drives, such as assign b = ~a; assign c = ~b;. Synthesis removes the chain, so a delay or a buffer
    written this way is not built; logic implied by a chain of inversions should be written as what it means. It is
    disabled by default; the do254 rule set enables it (SS1).

    **Violation**

    .. code-block:: systemverilog

       assign a_n = ~a;
       assign a_d = ~a_n;

    **Fix**

    .. code-block:: systemverilog

       assign a_d = a;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        dInverters = {}
        lAssignments = []
        for oAssign in oFile.nodes("ContinuousAssign"):
            for oAssignment in elements(oAssign.assignments):
                sTarget, sSource = inversion(oAssignment)
                if sTarget is not None:
                    dInverters[sTarget] = oAssignment
                    lAssignments.append((sTarget, sSource, oAssignment))
        for sTarget, sSource, oAssignment in lAssignments:
            if sSource in dInverters and dInverters[sSource] is not oAssignment:
                oToken = oFile.token_at(oAssignment.left.getFirstToken())
                if oToken is not None:
                    yield Problem(oToken, f"{sTarget} inverts {sSource}, which inverts a signal too: remove the chain of inverters")


def inversion(oAssignment):
    """(target, source) of an assignment of a signal to the inversion of another, both plain names; (None, None) else."""
    oLeft, oRight = getattr(oAssignment, "left", None), getattr(oAssignment, "right", None)
    if oLeft is None or oRight is None or oLeft.kind.name not in NAMES:
        return None, None
    while oRight.kind.name == "ParenthesizedExpression":
        oRight = oRight.expression
    if oRight.kind.name not in INVERSIONS:
        return None, None
    oOperand = oRight.operand
    while oOperand.kind.name == "ParenthesizedExpression":
        oOperand = oOperand.expression
    if oOperand.kind.name not in NAMES:
        return None, None
    return text(oLeft.identifier), text(oOperand.identifier)
