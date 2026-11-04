# -*- coding: utf-8 -*-

from mhsg import parser
from mhsg.rules.sv_spacing import Rule, kind, node

# The expressions in braces whose braces hold their contents without spaces
BRACED = (
    "ConcatenationExpression",
    "MultipleConcatenationExpression",
    "StreamingConcatenationExpression",
    "SimpleAssignmentPattern",
    "StructuredAssignmentPattern",
    "ReplicatedAssignmentPattern",
)


class rule_017(Rule):
    """
    This rule checks for no space after the opening brace and before the closing brace of a concatenation, a
    replication or an assignment pattern, as Verible's formatter does. Other braces, such as those of a struct, are
    not checked. A brace at the end or the start of a line, or followed by a comment, is not checked.

    **Violation**

    .. code-block:: systemverilog

       assign word = { high, low };
       assign mask = '{ default: 1'b0 };

    **Fix**

    .. code-block:: systemverilog

       assign word = {high, low};
       assign mask = '{default: 1'b0};
    """

    def __init__(self):
        super().__init__()
        self.solution = "Remove the space inside the braces"

    def spacing(self, oLeft, oRight):
        if isinstance(oRight, parser.comment):
            return None
        if kind(oLeft) in ("OpenBrace", "ApostropheOpenBrace") and node(oLeft) in BRACED:
            return (0, True)
        if kind(oRight) == "CloseBrace" and node(oRight) in BRACED:
            return (0, True)
        return None
