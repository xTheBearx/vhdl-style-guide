# -*- coding: utf-8 -*-

from mhsg import language, parser, violation
from mhsg.rules.token_indent import token_indent as Rule
from mhsg.svFile import tokens

lTokens = [tokens.token, parser.comment]
CLOSING = ("CloseParenthesis", "CloseBrace", "CloseBracket")
# The opening bracket of a port or parameter list may be on a line of its own at the level of the module
PORT_LISTS = (("AnsiPortList",), ("NonAnsiPortList",), ("ParameterPortList",))


class rule_002(Rule):
    """
    This rule checks that a continuation line, such as the second line of a long expression or of the arguments of a
    call, is indented more than the line that starts its statement. A line that starts with a closing bracket, with the
    opening bracket of a port list, with the next expression of a case item, or after an attribute on a line of its
    own, may be at the level of that line.

    The fix indents a continuation line like the continuation line before it in the statement, or else by
    **continuation_indent** levels, 2 by default, more than the line that starts its statement, as Verible's formatter
    does with its wrap width; a closing bracket goes to the level of that line.
    Continuation lines indented more, such as arguments aligned after their opening bracket, are left as they are.

    **Violation**

    .. code-block:: systemverilog

       assign valid_o = req_i &
       ready_i;

    **Fix**

    .. code-block:: systemverilog

       assign valid_o = req_i &
               ready_i;
    """

    def __init__(self):
        super().__init__(lTokens)
        self.languages = (language.SYSTEMVERILOG,)
        self.continuation_indent = 2
        self.configuration.append("continuation_indent")

    def _get_tokens_of_interest(self, oFile):
        if getattr(oFile, "syntax_errors", None):
            return []
        lReturn = []
        iBase = None
        iStatement = 0
        # The last token of code before each token, to tell a line that continues a list of case item expressions
        dPrevious = {}
        oPrevious = None
        for oItem in oFile.lAllObjects:
            if isinstance(oItem, tokens.token):
                dPrevious[id(oItem)] = oPrevious
                oPrevious = oItem
        for oToi in oFile.get_tokens_at_beginning_of_line_matching(self.lTokens):
            lLine = oToi.get_tokens()
            oToken = lLine[-1]
            if isinstance(oToken, parser.comment):
                continue
            if isinstance(oToken, (tokens.preprocessor, tokens.unclassified)):
                continue
            if oToken.get_indent() is not None:
                iBase = oToken.get_indent()
                iStatement += 1
                continue
            oBefore = dPrevious.get(id(oToken))
            lBefore = [oBefore, dPrevious.get(id(oBefore))]
            if iBase is None or any(isinstance(o, (tokens.preprocessor, tokens.unclassified)) for o in lBefore):
                # After a macro, whose arguments are not parsed, and the semicolon that may end it, the level is not
                # known until a line has one again
                iBase = None
                continue
            oToi.dMetaData["base"] = iBase
            oToi.dMetaData["statement"] = iStatement
            # A closing bracket, the next expression of a case item, or what follows an attribute on a line of its own,
            # may be at the level of the statement
            oToi.dMetaData["closing"] = (
                getattr(oToken, "kind", None) in CLOSING
                or (getattr(oBefore, "kind", None) == "Comma" and tuple(getattr(oBefore, "syntax", ()))[-1:] == ("StandardCaseItem",))
                or (getattr(oBefore, "kind", None) == "CloseParenthesis" and tuple(getattr(oBefore, "syntax", ()))[-1:] == ("AttributeInstance",))
                or (getattr(oToken, "kind", None) in ("OpenParenthesis", "Hash") and tuple(getattr(oToken, "syntax", ()))[-1:] in PORT_LISTS)
            )
            lReturn.append(oToi)
        return lReturn

    def _analyze(self, lToi):
        # The indent of the last continuation line of each statement, after the fix
        dLast = {}
        for oToi in lToi:
            lLine = oToi.get_tokens()
            sWhitespace = lLine[0].get_value() if len(lLine) == 2 else ""
            if "\t" in sWhitespace or self.indent_style != "spaces":
                continue
            iBase = oToi.dMetaData["base"] * self.indent_size
            bClosing = oToi.dMetaData["closing"]
            iStatement = oToi.dMetaData["statement"]
            if len(sWhitespace) >= iBase + (0 if bClosing else 1):
                if not bClosing:
                    dLast[iStatement] = len(sWhitespace)
                continue
            # Like the continuation line before it, else continuation_indent levels in
            iWanted = iBase if bClosing else dLast.get(iStatement, iBase + int(self.continuation_indent) * self.indent_size)
            if not bClosing:
                dLast[iStatement] = iWanted
            oViolation = violation.New(oToi.get_line_number(), oToi, f"Indent the continuation line by {iWanted} spaces")
            oViolation.set_action(iWanted)
            self.add_violation(oViolation)

    def _fix_violation(self, oViolation):
        lLine = oViolation.get_tokens()
        iWanted = oViolation.get_action()
        oToken = lLine[-1]
        lNew = ([parser.whitespace(" " * iWanted)] if iWanted > 0 else []) + [oToken]
        oViolation.set_tokens(lNew)
