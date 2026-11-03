# -*- coding: utf-8 -*-

from mhsg.lint import model
from mhsg.lint.rule import Rule


class rule_023(Rule):
    """
    This rule checks that an entity with generics checks their values with an assertion.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254_plus rule set.

    A generic value outside the range a design supports, such as a width of zero, otherwise goes unnoticed until the hardware fails.
    The rule accepts any assert statement in the file, in the entity or in an architecture.

    **Violation**

    .. code-block:: vhdl

       entity fifo is
         generic (
           DEPTH : positive
         );

    **Fix**

    .. code-block:: vhdl

       assert DEPTH mod 2 = 0
         report "DEPTH must be a power of two"
         severity failure;
    """

    def __init__(self):
        super().__init__()
        self.solution = "Check the generics with an assertion"

    def check(self, oModel, oFile):
        lTokens = oFile.lAllObjects
        if any(model.kind(o)[0] in ("assertion", "concurrent_assertion_statement", "assertion_statement") for o in lTokens):
            return
        sEntity = None
        for iIndex, oToken in enumerate(lTokens):
            tKind = model.kind(oToken)
            if tKind == ("entity_declaration", "identifier"):
                sEntity = oToken.get_value()
            elif tKind == ("generic_clause", "generic_keyword") and sEntity is not None:
                self.report(oFile, iIndex, f"Check the generics of entity {sEntity} with an assertion")
                sEntity = None
            elif tKind == ("entity_declaration", "semicolon"):
                sEntity = None
