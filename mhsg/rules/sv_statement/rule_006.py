# -*- coding: utf-8 -*-

from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_006(TreeRule, structure.Rule):
    """
    This rule checks for empty branches of if and case statements, such as a case item with only a semicolon, as
    the STARC guide asks (2.7.2.3). It is disabled by default; the starc rule set enables it.

    **Violation**

    .. code-block:: systemverilog

       Idle: ;

    **Fix**

    .. code-block:: systemverilog

       Idle: state_d = Busy;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"

    def problems(self, oFile):
        for sKind, sField in (("StandardCaseItem", "clause"), ("DefaultCaseItem", "clause"), ("ConditionalStatement", "statement"), ("ElseClause", "clause")):
            for oNode in oFile.nodes(sKind):
                oClause = getattr(oNode, sField, None)
                if oClause is not None and oClause.kind.name == "EmptyStatement":
                    oToken = oFile.token_at(oNode.getFirstToken())
                    if oToken is not None:
                        yield Problem(oToken, "Remove the empty branch or give it a statement")
