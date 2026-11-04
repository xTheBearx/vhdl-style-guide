# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import has_x_or_z, text
from mhsg.rules.sv_tree import Problem, TreeRule

LITERALS = ("IntegerVectorExpression", "UnbasedUnsizedLiteralExpression")


class rule_006(TreeRule, structure.Rule):
    """
    This rule checks for literals with x or z digits, as the STARC guide asks (2.10.1.6, and 2.1.6.5 for indexes).
    The don't-care of the default item of a case statement (2.8.3.1) and the wildcards of casez and casex items are
    allowed; comparisons with x or z are checked by sv_literal_005. It is disabled by default; the starc rule set
    enables it.

    **Violation**

    .. code-block:: systemverilog

       assign y = 8'bxxxx_0000;

    **Fix**

    .. code-block:: systemverilog

       assign y = 8'b0000_0000;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for oNode in oFile.nodes(*LITERALS):
            if not has_x_or_z(oNode) or allowed(oNode):
                continue
            oToken = oFile.token_at(oNode.getFirstToken())
            if oToken is not None:
                yield Problem(oToken, "Do not use x or z in a literal")


def allowed(oNode):
    """A literal of a default case item, of a casez or casex item, or of a comparison, which sv_literal_005 checks."""
    oParent = oNode.parent
    while oParent is not None:
        sKind = oParent.kind.name
        if sKind == "DefaultCaseItem":
            return True
        if sKind == "StandardCaseItem":
            oCase = oParent.parent
            return oCase is not None and text(oCase.caseKeyword) in ("casez", "casex") and is_label(oNode, oParent)
        if sKind in ("EqualityExpression", "InequalityExpression", "CaseEqualityExpression", "CaseInequalityExpression"):
            return True
        oParent = oParent.parent
    return False


def is_label(oNode, oItem):
    """True when a node is in the expressions of a case item, not in its statement."""
    oParent = oNode
    while oParent is not None and oParent.parent is not oItem:
        oParent = oParent.parent
    return oParent is not None and oParent is not oItem.clause
