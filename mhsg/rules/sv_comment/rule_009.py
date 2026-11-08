# -*- coding: utf-8 -*-

import re

from mhsg import parser
from mhsg.rule_group import structure
from mhsg.rules.sv_tree import Problem, TreeRule

HIDDEN = re.compile(
    r"^(?://|/\*)\s*(?:(synthesis|pragma|synopsys|rtl_synthesis|cadence|xilinx|altera)\s+translate_off\b"
    r"|(?:(?:pragma|vcs|cadence)\s+)?coverage\s+off\b|verilator\s+coverage_off\b)",
    re.IGNORECASE,
)


class rule_009(TreeRule, structure.Rule):
    """
    This rule checks for regions of code hidden from synthesis or from coverage. It is disabled by default; the
    do254_plus rule set enables it (PRAGMA).

    Code between // synopsys translate_off and translate_on, or under an ifndef SYNTHESIS directive, is simulated but not
    synthesized, and code between // coverage off and coverage on is not counted in coverage. Each such region should
    be justified, with a waiver that gives the reason.

    **Violation**

    .. code-block:: systemverilog

       // synopsys translate_off
       initial $display("width %0d", Width);
       // synopsys translate_on
    """

    def __init__(self):
        super().__init__()
        self.disable = True
        self.solution = "Justify or remove the region"

    def problems(self, oFile):
        lTokens = oFile.lAllObjects
        for iIndex, oToken in enumerate(lTokens):
            if isinstance(oToken, parser.comment):
                oMatch = HIDDEN.search(oToken.get_value() or "")
                if oMatch is not None:
                    sWhat = "synthesis" if oMatch.group(1) else "coverage"
                    yield Problem(oToken, f"Code from here is hidden from {sWhat}; justify the region")
            elif (oToken.get_value() or "") == "`ifndef" and macro_after(lTokens, iIndex) == "SYNTHESIS":
                yield Problem(oToken, "Code from here is hidden from synthesis; justify the region")


def macro_after(lTokens, iIndex):
    """The name of the macro a conditional directive tests."""
    for oToken in lTokens[iIndex + 1 : iIndex + 4]:
        if not isinstance(oToken, (parser.whitespace, parser.comment)):
            return oToken.get_value()
    return None
