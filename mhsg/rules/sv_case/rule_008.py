# -*- coding: utf-8 -*-

import re

from mhsg.rule_group import structure
from mhsg.rules.sv_nodes import source, text
from mhsg.rules.sv_tree import Problem, TreeRule, elements

LITERALS = ("IntegerLiteralExpression", "IntegerVectorExpression", "UnbasedUnsizedLiteralExpression")


class rule_008(TreeRule, structure.Rule):
    """
    This rule checks that the items of a case statement on a state, a selector matching **state_pattern**, a regular
    expression matched ignoring case, by default names holding state, are named encodings, parameters or enum values,
    not numbers, as the STARC guide asks (2.11.1.3, 2.11.4.2). It is disabled by default; the starc rule set enables
    it.

    **Violation**

    .. code-block:: systemverilog

       case (state)
           2'b00: next_state = 2'b01;

    **Fix**

    .. code-block:: systemverilog

       case (state)
           Idle: next_state = Busy;
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "See the rule documentation"
        self.state_pattern = ".*state.*"
        self.configuration.append("state_pattern")

    def problems(self, oFile):
        for oCase in state_cases(oFile, self.state_pattern):
            for oItem in elements(oCase.items):
                if oItem.kind.name != "StandardCaseItem":
                    continue
                for oExpression in elements(oItem.expressions):
                    if oExpression.kind.name in LITERALS:
                        oToken = oFile.token_at(oExpression.getFirstToken())
                        if oToken is not None:
                            yield Problem(oToken, f"Name the state encoding {source(oExpression)} with a parameter")


def state_cases(oFile, sPattern):
    """The case statements whose selector is a name matching a pattern, ignoring case."""
    for oCase in oFile.nodes("CaseStatement"):
        oExpression = oCase.expr
        while oExpression is not None and oExpression.kind.name == "ParenthesizedExpression":
            oExpression = oExpression.expression
        if (
            oExpression is not None
            and oExpression.kind.name in ("IdentifierName", "IdentifierSelectName")
            and re.fullmatch(sPattern, text(oExpression.identifier), re.IGNORECASE)
        ):
            yield oCase
