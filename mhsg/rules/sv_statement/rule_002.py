# -*- coding: utf-8 -*-

from mhsg import parser
from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule


class rule_002(TreeRule, structure.Rule):
    """
    This rule checks for consecutive null statements, such as ;;.

    **Violation**

    .. code-block:: systemverilog

       count_d = count_q + 1;;

    **Fix**

    .. code-block:: systemverilog

       count_d = count_q + 1;
    """

    def __init__(self):
        super().__init__()
        self.fixable = True
        self.solution = "Remove the null statement"

    def problems(self, oFile):
        dPrevious = {}
        dSpaceBefore = {}
        oPrevious = None
        oLast = None
        for oToken in oFile.lAllObjects:
            if not isinstance(oToken, (parser.whitespace, parser.carriage_return, parser.blank_line, parser.comment)):
                dPrevious[id(oToken)] = oPrevious
                oPrevious = oToken
                if isinstance(oLast, parser.whitespace):
                    dSpaceBefore[id(oToken)] = oLast
            oLast = oToken
        for oNode in oFile.nodes("EmptyStatement"):
            oToken = oFile.token_at(oNode.semicolon)
            if oToken is None or oNode.label is not None or len(oNode.attributes):
                continue
            oBefore = dPrevious.get(id(oToken))
            if oBefore is not None and oBefore.get_value() == ";":
                # The space before the null statement goes with it
                yield Problem(dSpaceBefore.get(id(oToken), oToken), self.solution, oToken)

    def _fix_violation(self, oViolation):
        oViolation.set_tokens([])
