# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import has_x_or_z, text
from mhsg.rules.sv_statement.rule_017 import high_impedance
from mhsg.rules.sv_tree import Problem, TreeRule, descendants, elements

ASSIGNMENTS = ("NonblockingAssignmentExpression", "AssignmentExpression")


class rule_018(TreeRule, structure.Rule):
    """
    This rule checks that tri-state signals, the signals the file assigns a value with z digits, are not tested in if
    conditions or used as case selectors, as the STARC guide asks (2.5.1.7, 2.5.1.8, 2.5.1.9). A case statement whose
    default assigns x may use them. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       assign bus = oe ? data : 'z;
       always_comb if (bus) y = 1'b1; else y = 1'b0;

    **Fix**

    Test the signal that drives the bus, data, instead.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        setTristate = set()
        for oNode in oFile.nodes(*ASSIGNMENTS):
            if oNode.left is not None and oNode.right is not None and any(high_impedance(o) for o in [oNode.right, *descendants(oNode.right)]):
                setTristate.add(text(oNode.left.getFirstToken()))
        if not setTristate:
            return
        lTested = [o.predicate for o in oFile.nodes("ConditionalStatement")]
        lTested += [o.expr for o in oFile.nodes("CaseStatement") if not default_assigns_x(o)]
        for oTested in lTested:
            for oName in [oTested, *descendants(oTested)]:
                if oName.kind.name in ("IdentifierName", "IdentifierSelectName") and text(oName.identifier) in setTristate:
                    oToken = oFile.token_at(oName.identifier)
                    if oToken is not None:
                        yield Problem(oToken, f"Do not test the tri-state signal {text(oName.identifier)}")
                    break


def default_assigns_x(oCase):
    """True for a case statement, not casex or casez, whose default item assigns a value with x digits."""
    if text(oCase.caseKeyword) != "case":
        return False
    for oItem in elements(oCase.items):
        if oItem.kind.name == "DefaultCaseItem":
            return any(has_x_or_z(o) and "x" in str(o).lower() for o in descendants(oItem))
    return False
