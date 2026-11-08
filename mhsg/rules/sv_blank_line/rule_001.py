# -*- coding: utf-8 -*-

from mhsg import language, parser, violation
from mhsg.rule_group import blank_line
from mhsg.vhdlFile.extract import tokens


class rule_001(blank_line.Rule):
    """
    This rule checks for blank lines at the end of a file, which Verible's formatter removes.

    **Violation**

    .. code-block:: systemverilog

       endmodule



    **Fix**

    .. code-block:: systemverilog

       endmodule
    """

    def __init__(self):
        super().__init__()
        self.languages = language.VERILOG_LANGUAGES
        self.configuration_documentation_link = None
        self.solution = "Remove blank lines at the end of the file"

    def _get_tokens_of_interest(self, oFile):
        lTokens = oFile.lAllObjects
        iLast = None
        for iToken in range(len(lTokens) - 1, -1, -1):
            if not isinstance(lTokens[iToken], (parser.carriage_return, parser.blank_line, parser.whitespace)):
                iLast = iToken
                break
        # The line end of the last line of the file stays
        iStart = (iLast + 2) if iLast is not None else 0
        if iLast is None or iStart >= len(lTokens) or not any(isinstance(o, parser.blank_line) for o in lTokens[iStart:]):
            return []
        return [tokens.New(iStart, oFile.oTokenMap.get_line_number_of_index(iStart), lTokens[iStart:])]

    def _analyze(self, lToi):
        for oToi in lToi:
            self.add_violation(violation.New(oToi.get_line_number(), oToi, self.solution))

    def _fix_violation(self, oViolation):
        oViolation.set_tokens([])
