# -*- coding: utf-8 -*-

import re

from mhsg import parser
from mhsg.lint.rule import Rule

reHidden = re.compile(r"--\s*(synthesis|pragma|synopsys|rtl_synthesis)\s+translate_off\b|--\s*(coverage|pragma\s+coverage)\s+off\b", re.IGNORECASE)


class rule_015(Rule):
    """
    This rule checks for regions of code hidden from synthesis or from coverage by pragmas.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254_plus rule set.

    Code between :code:`-- synthesis translate_off` and :code:`translate_on` is simulated but not synthesized,
    and code between :code:`-- coverage off` and :code:`coverage on` is not counted in coverage.
    Each such region should be justified, for example with a comment on the same line as the pragma.

    **Violation**

    .. code-block:: vhdl

       -- synthesis translate_off
       assert width > 0 report "width must be positive";
       -- synthesis translate_on
    """

    def __init__(self):
        super().__init__()
        self.solution = "Justify or remove the region"

    def check(self, oModel, oFile):
        for iIndex, oToken in enumerate(oFile.lAllObjects):
            if isinstance(oToken, parser.comment) or type(oToken).__module__.endswith("pragma"):
                oMatch = reHidden.search(oToken.get_value() or "")
                if oMatch is not None:
                    sWhat = "synthesis" if oMatch.group(1) else "coverage"
                    self.report(oFile, iIndex, f"Code from here is hidden from {sWhat}; justify the region")
