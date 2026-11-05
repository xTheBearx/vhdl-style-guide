# -*- coding: utf-8 -*-
"""Base class of the lint rules that report warnings of slang's elaboration and analysis."""

from mhsg import language
from mhsg.lint.rule import Rule as LintRule

# The warnings of mhsg itself about the parameters of the modules of a run, see svFile/project.py, sv_lint_014 and
# sv_lint_015
PARTIAL_OVERRIDE = "MhsgPartialParameterOverride"
REUSED_PARAMETER = "MhsgReusedParameterName"


class Rule(LintRule):
    """Reports the slang warnings whose names the rule accepts, with slang's message."""

    def __init__(self):
        super().__init__()
        self.languages = (language.SYSTEMVERILOG,)

    def accepts(self, sName):
        raise NotImplementedError

    def check(self, oModel, oFile):
        if oModel is None or getattr(oFile, "syntax_errors", None):
            return
        dIndexes = {id(o): i for i, o in enumerate(oFile.lAllObjects)}
        for oDiagnostic in oModel.named(self.accepts):
            oToken = oFile.token_at_or_after(oDiagnostic.offset)
            if oToken is not None and id(oToken) in dIndexes:
                self.report(oFile, dIndexes[id(oToken)], self.message(oDiagnostic))

    def message(self, oDiagnostic):
        """The message of a finding: slang's message, starting with a capital."""
        return oDiagnostic.message[:1].upper() + oDiagnostic.message[1:]
