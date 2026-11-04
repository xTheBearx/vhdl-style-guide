# -*- coding: utf-8 -*-
"""
Base class of the rules on the spaces between two tokens of a SystemVerilog line.

A rule says, for two tokens next to each other on a line, how many spaces they need: exactly, as no space before
a comma, or at least, as around a binary operator, where code aligned in columns has more. The spacing follows
Verible's formatter.

An escaped identifier, such as \\bus+index, ends at whitespace, so it keeps one space where a rule wants none.
Tokens in inactive `ifdef branches and in the arguments of macros are not parsed, and macro uses expand to code mhsg
does not see, so pairs with them are left alone; only a comment may follow a macro use. A file with syntax errors is
left alone, as its tokens may be classified wrongly near the errors, see sv_syntax_001.
"""

import importlib

from mhsg import language, parser, violation
from mhsg.rule_group import whitespace
from mhsg.rules.sv_tree import before_errors, first_error_line
from mhsg.svFile import tokens
from mhsg.vhdlFile.extract import tokens as extract_tokens

# mhsg.svFile exports the class svFile under the name of its module
svFile = importlib.import_module("mhsg.svFile.svFile")

# Syntax nodes holding the index or the range of a select or a dimension, where Verible allows operators without
# spaces, as in a[i+1]
BRACKETS = ("ElementSelect", "VariableDimension")
# Expressions whose operator token is not a binary operator
NOT_BINARY = ("PostincrementExpression", "PostdecrementExpression", "PreincrementExpression", "PredecrementExpression", "StreamingConcatenationExpression")


class Rule(whitespace.Rule):
    """Checks the spaces between two tokens on a line of a SystemVerilog file."""

    def __init__(self):
        super().__init__()
        self.languages = (language.SYSTEMVERILOG,)
        self.configuration_documentation_link = None

    def spacing(self, oLeft, oRight):
        """Returns (spaces, exact) for two tokens next to each other on a line, or None if the rule does not apply."""
        raise NotImplementedError

    def _get_tokens_of_interest(self, oFile):
        lReturn = []
        lTokens = oFile.lAllObjects
        iPrevious = None
        for iToken, oToken in enumerate(lTokens):
            if isinstance(oToken, parser.carriage_return):
                iPrevious = None
                continue
            if isinstance(oToken, (parser.whitespace, parser.blank_line)):
                continue
            if iPrevious is not None and is_code(lTokens[iPrevious]) and (is_code(oToken) or isinstance(oToken, parser.comment)):
                if (
                    isinstance(oToken, parser.comment)
                    or not isinstance(lTokens[iPrevious], tokens.preprocessor)
                    and not isinstance(oToken, tokens.preprocessor)
                ):
                    tSpacing = self.spacing(lTokens[iPrevious], oToken)
                    if tSpacing is not None and tSpacing[0] == 0 and lTokens[iPrevious].get_value().startswith("\\"):
                        # An escaped identifier ends at whitespace, so it keeps one space, as Verible's formatter does
                        tSpacing = (1, True)
                    if tSpacing is not None:
                        iLine = oFile.oTokenMap.get_line_number_of_index(iToken)
                        oToi = extract_tokens.New(iPrevious, iLine, lTokens[iPrevious : iToken + 1])
                        oToi.dMetaData["spacing"] = tSpacing
                        lReturn.append(oToi)
            iPrevious = iToken
        return before_errors(oFile, lReturn)

    def _analyze(self, lToi):
        for oToi in lToi:
            lTokens = oToi.get_tokens()
            iSpaces, bExact = oToi.dMetaData["spacing"]
            sWhitespace = lTokens[1].get_value() if len(lTokens) == 3 else ""
            if "\t" in sWhitespace:
                # whitespace_002 replaces tabs first
                continue
            if (bExact and len(sWhitespace) != iSpaces) or (not bExact and len(sWhitespace) < iSpaces):
                oViolation = violation.New(oToi.get_line_number(), oToi, self.solution)
                oViolation.set_action(iSpaces)
                self.add_violation(oViolation)

    def fix(self, oFile, dFixOnly=None):
        if first_error_line(oFile) is not None:
            return
        super().fix(oFile, dFixOnly)
        # A comment continuing a trailing comment moves with it
        if self.fixable and svFile.realign_comment_continuations(oFile.lAllObjects):
            oFile.update_token_map()

    def _fix_violation(self, oViolation):
        lTokens = oViolation.get_tokens()
        iSpaces = oViolation.get_action()
        lNew = [lTokens[0]]
        if iSpaces > 0:
            lNew.append(parser.whitespace(" " * iSpaces))
        lNew.append(lTokens[-1])
        oViolation.set_tokens(lNew)


def is_code(oToken):
    """True for a token of parsed code or a directive, False for unparsed code."""
    return isinstance(oToken, tokens.token) and not isinstance(oToken, tokens.unclassified)


def kind(oToken):
    """The slang token kind, such as Comma, or None for whitespace and comments."""
    return getattr(oToken, "kind", None)


def node(oToken, iLevel=1):
    """The kind of the syntax node holding a token, or of one of its parents with iLevel > 1, or None."""
    tSyntax = getattr(oToken, "syntax", ())
    return tSyntax[-iLevel] if len(tSyntax) >= iLevel else None


def field(oToken):
    return getattr(oToken, "field", None)


def in_brackets(oToken):
    return any(s in BRACKETS for s in getattr(oToken, "syntax", ()))


def is_binary_operator(oToken):
    """True for a binary or assignment operator, or the ? and : of a conditional expression, outside brackets."""
    sNode = node(oToken)
    if sNode is None or in_brackets(oToken):
        return False
    if field(oToken) == "operatorToken":
        return sNode.endswith("Expression") and not sNode.startswith("Unary") and sNode not in NOT_BINARY
    if field(oToken) == "equals":
        return True
    return sNode == "ConditionalExpression" and field(oToken) in ("question", "colon")


def is_unary_operator(oToken):
    return field(oToken) == "operatorToken" and (node(oToken) or "").startswith("Unary")


# Keywords followed by one space and a parenthesis
CONTROL_KEYWORDS = (
    "IfKeyword",
    "ForKeyword",
    "ForeachKeyword",
    "WhileKeyword",
    "RepeatKeyword",
    "WaitKeyword",
    "CaseKeyword",
    "CaseZKeyword",
    "CaseXKeyword",
    "RandCaseKeyword",
)
ALWAYS_KEYWORDS = ("AlwaysKeyword", "AlwaysFFKeyword", "AlwaysCombKeyword", "AlwaysLatchKeyword")
CASE_ITEMS = ("StandardCaseItem", "DefaultCaseItem", "PatternCaseItem")
