# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule

INTEGER_TYPES = ("integer", "natural", "positive")
DECLARATIONS = ("signal_declaration", "interface_signal_declaration", "interface_unknown_declaration")


class rule_016(Rule):
    """
    This rule checks that integer signals and ports have a range.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254_plus rule set.

    An integer, natural or positive signal without a range synthesizes to 32 bits and hides its real width.
    Constants, generics and variables are not checked.

    **Violation**

    .. code-block:: vhdl

       signal count : natural;

    **Fix**

    .. code-block:: vhdl

       signal count : natural range 0 to 15;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Add a range"

    def check(self, oModel, oFile):
        lTokens = oFile.lAllObjects
        bType = False
        bPortClause = False
        for iIndex, oToken in enumerate(lTokens):
            tKind = model.kind(oToken)
            if tKind == ("port_clause", "port_keyword"):
                bPortClause = True
            elif tKind == ("port_clause", "close_parenthesis"):
                bPortClause = False
            # Signals, and ports; generics and subprogram parameters use the same interface declarations
            if (tKind == ("signal_declaration", "colon")) or (bPortClause and tKind[0] in DECLARATIONS[1:] and tKind[1] == "colon"):
                bType = True
            elif bType and tKind == ("type_mark", "name"):
                bType = False
                if (oToken.get_value() or "").lower() in INTEGER_TYPES and not has_range(lTokens, iIndex):
                    self.report(oFile, iIndex, f"Give the {oToken.get_value().lower()} a range, such as range 0 to 15")
            elif isinstance(oToken, model.parser.semicolon):
                bType = False


def has_range(lTokens, iIndex):
    """Returns True if the type mark at iIndex is followed by a range constraint."""
    for oToken in lTokens[iIndex + 1 :]:
        if model.is_trivia(oToken):
            continue
        return (oToken.get_value() or "").lower() == "range"
    return False
