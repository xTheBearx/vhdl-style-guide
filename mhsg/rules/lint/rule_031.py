# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule

# Vector types whose index ranges should all run one way
VECTOR_TYPES = ("std_logic_vector", "std_ulogic_vector", "unsigned", "signed", "bit_vector", "ufixed", "sfixed")


class rule_031(Rule):
    """
    This rule checks that the ranges of vectors run in one direction, downto by default.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254 rule set (SS21).

    A vector declared with :code:`to` next to vectors declared with :code:`downto` reverses the order of its bits when
    the two are assigned to each other, a mistake that is easy to miss. The rule checks the ranges of
    std_logic_vector, unsigned, signed and the other vector types; arrays of other types, such as memories, may run
    either way. The direction option sets the direction, downto or to.

    **Violation**

    .. code-block:: vhdl

       signal data : std_logic_vector(0 to 7);

    **Fix**

    .. code-block:: vhdl

       signal data : std_logic_vector(7 downto 0);
    """

    def __init__(self):
        super().__init__()
        self.solution = "Use one direction for vector ranges"
        self.direction = "downto"
        self.configuration.append("direction")

    def check(self, oModel, oFile):
        lTokens = oFile.lAllObjects
        for iIndex, oToken in enumerate(lTokens):
            if model.kind(oToken) != ("type_mark", "name") or (oToken.get_value() or "").lower() not in VECTOR_TYPES:
                continue
            iDirection = range_direction(lTokens, iIndex)
            if iDirection is not None and lTokens[iDirection].get_value().lower() != str(self.direction).lower():
                self.report(oFile, iDirection, f"Declare the {oToken.get_value().lower()} with {self.direction}, like the other vectors")


def range_direction(lTokens, iIndex):
    """Returns the index of the direction keyword of the range that follows the type mark at iIndex, or None."""
    iDepth = 0
    for iNext in range(iIndex + 1, len(lTokens)):
        oToken = lTokens[iNext]
        if model.is_trivia(oToken):
            continue
        if iDepth == 0 and not isinstance(oToken, model.parser.open_parenthesis):
            return None
        if isinstance(oToken, model.parser.open_parenthesis):
            iDepth += 1
        elif isinstance(oToken, model.parser.close_parenthesis):
            iDepth -= 1
            if iDepth == 0:
                return None
        elif iDepth == 1 and model.kind(oToken)[0] == "direction":
            return iNext
    return None
