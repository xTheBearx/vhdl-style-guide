# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import has_x_or_z, text
from mhsg.rules.sv_statement.rule_018 import default_assigns_x
from mhsg.rules.sv_tree import Problem, TreeRule, descendants

ASSIGNMENTS = ("NonblockingAssignmentExpression", "AssignmentExpression")


class rule_028(TreeRule, structure.Rule):
    """
    This rule checks that don't care signals, the signals the file assigns a value with x digits, are not tested in
    if conditions or used as case selectors, as the STARC guide asks (2.8.3.4, 2.8.3.6, 2.8.3.7). A case statement
    whose default assigns x may use them. It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       default: sel = 2'bxx;
       ...
       if (sel == 2'b01) y = a;

    **Fix**

    Assign sel a value in every branch, or do not test it.
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        setDontCare = set()
        for oNode in oFile.nodes(*ASSIGNMENTS):
            if (
                oNode.left is not None
                and oNode.right is not None
                and any(has_x_or_z(o) and "x" in str(o).lower() for o in [oNode.right, *descendants(oNode.right)])
            ):
                setDontCare.add(text(oNode.left.getFirstToken()))
        if not setDontCare:
            return
        lTested = [o.predicate for o in oFile.nodes("ConditionalStatement")]
        lTested += [o.expr for o in oFile.nodes("CaseStatement") if not default_assigns_x(o)]
        for oTested in lTested:
            for oName in [oTested, *descendants(oTested)]:
                if oName.kind.name in ("IdentifierName", "IdentifierSelectName") and text(oName.identifier) in setDontCare:
                    oToken = oFile.token_at(oName.identifier)
                    if oToken is not None:
                        yield Problem(oToken, f"Do not test {text(oName.identifier)}, which may be assigned x")
                    break
