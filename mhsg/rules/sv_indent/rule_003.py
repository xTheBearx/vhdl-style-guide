# -*- coding: utf-8 -*-

from mhsg import language, parser, violation
from mhsg.rules.sv_tree import before_errors
from mhsg.rules.token_indent import token_indent as Rule
from mhsg.svFile import tokens

lTokens = [tokens.token, parser.comment]
CONDITIONAL = ("`ifdef", "`ifndef", "`elsif", "`else", "`endif")


class rule_003(Rule):
    """
    This rule checks the indent of preprocessor directives and of macro uses that start a line.

    As Verible's formatter does, the conditional directives, :code:`\\`ifdef`, :code:`\\`ifndef`, :code:`\\`elsif`,
    :code:`\\`else` and :code:`\\`endif`, are at column 0, wherever they are; with **conditional_indent** set to
    code, they are indented like the other directives. The other directives, such as :code:`\\`define`,
    :code:`\\`include` and :code:`\\`undef`, and macro uses that start a line are at the level of the code around
    them: that of the next line of code, or one level in when that line closes a block, such as end or endmodule.
    The code between conditional directives is indented as if they were not there, see sv_indent_001.
    The lines a :code:`\\`define` continues with a backslash are not checked.

    **Violation**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i) begin
           `ifdef RESET_ALL
           a_q <= '0;
           `endif
             `ASSERT(a_q_known, !$isunknown(a_q))
       end

    **Fix**

    .. code-block:: systemverilog

       always_ff @(posedge clk_i) begin
       `ifdef RESET_ALL
           a_q <= '0;
       `endif
           `ASSERT(a_q_known, !$isunknown(a_q))
       end
    """

    def __init__(self):
        super().__init__(lTokens)
        self.languages = language.VERILOG_LANGUAGES
        self.conditional_indent = "zero"
        self.configuration.append("conditional_indent")

    def _get_tokens_of_interest(self, oFile):
        lLines = oFile.get_tokens_at_beginning_of_line_matching(self.lTokens)
        # The level of the code that starts each line, None for a line that is not code with a known level
        lLevels = []
        for oToi in lLines:
            oToken = oToi.get_tokens()[-1]
            if isinstance(oToken, (parser.comment, tokens.preprocessor, tokens.unclassified)) or oToken.get_indent() is None:
                lLevels.append(None)
            else:
                lLevels.append(oToken.get_indent() + (1 if getattr(oToken, "closing", False) else 0))
        lReturn = []
        bContinued = False
        dIndex = {id(o): i for i, o in enumerate(oFile.lAllObjects)}
        for iIndex, oToi in enumerate(lLines):
            oToken = oToi.get_tokens()[-1]
            bInBody = bContinued
            bContinued = line_continues(oFile, oToi, dIndex)
            if bInBody or not isinstance(oToken, tokens.preprocessor):
                continue
            sText = oToken.get_value().split("(")[0].strip().lower()
            if sText in CONDITIONAL and str(self.conditional_indent).lower() != "code":
                iLevel = 0
            else:
                iLevel = next((i for i in lLevels[iIndex + 1 :] if i is not None), 0)
            oToi.dMetaData["level"] = iLevel
            lReturn.append(oToi)
        return before_errors(oFile, lReturn)

    def _analyze(self, lToi):
        for oToi in lToi:
            lLine = oToi.get_tokens()
            sWhitespace = lLine[0].get_value() if len(lLine) == 2 else ""
            iLevel = oToi.dMetaData["level"]
            sWanted = "\t" * iLevel if self.indent_style != "spaces" else " " * (iLevel * self.indent_size)
            if sWhitespace == sWanted:
                continue
            sUnit = "spaces" if self.indent_style == "spaces" else "tabs"
            sSolution = f"Indent the directive by {len(sWanted)} {sUnit}" if sWanted else "Start the directive at column 0"
            oViolation = violation.New(oToi.get_line_number(), oToi, sSolution)
            oViolation.set_action(sWanted)
            self.add_violation(oViolation)

    def _fix_violation(self, oViolation):
        lLine = oViolation.get_tokens()
        sWanted = oViolation.get_action()
        oViolation.set_tokens(([parser.whitespace(sWanted)] if sWanted else []) + [lLine[-1]])


def line_continues(oFile, oToi, dIndex=None):
    """
    Whether the line of a token ends with a backslash, which continues a `define on the next line. dIndex, {id of a
    token: its index in the file}, saves looking the token up.
    """
    oToken = oToi.get_tokens()[-1]
    lObjects = oFile.lAllObjects
    iIndex = dIndex.get(id(oToken)) if dIndex is not None else next((i for i, o in enumerate(lObjects) if o is oToken), None)
    if iIndex is None:
        return False
    for iItem in range(iIndex, len(lObjects)):
        oItem = lObjects[iItem]
        if isinstance(oItem, parser.carriage_return):
            return False
        sValue = oItem.get_value() if hasattr(oItem, "get_value") else ""
        if isinstance(sValue, str) and sValue.rstrip().endswith("\\") and getattr(oItem, "kind", "") == "LineContinuation":
            return True
    return False
