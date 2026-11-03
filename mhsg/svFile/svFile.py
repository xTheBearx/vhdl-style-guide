# -*- coding: utf-8 -*-
"""
SystemVerilog and Verilog files, read with slang (pyslang).

The tokens come from slang's lexer run on the text as written, before preprocessing, so the file is kept exactly,
with its macro uses, directives and inactive `ifdef branches. Each token is then looked up in slang's syntax tree by
its offset, which tells the syntax node and field it belongs to; tokens the tree does not have, in inactive branches
or macro arguments, are unclassified.

svFile shares the methods of vhdlFile that work on the list of tokens, such as get_tokens_matching and get_lines,
so the fix pipeline and the rules that only look at whitespace, comments and lines work unchanged. Rules declare the
languages they apply to, see rule.Rule.languages.
"""

import importlib

import pyslang

# The submodules of pyslang are made when its extension loads, so pylint cannot find them
from pyslang.parsing import (  # pylint: disable=import-error
    Lexer,
    LexerOptions,
    Token,
    TokenKind,
)
from pyslang.syntax import SyntaxNode, SyntaxTree  # pylint: disable=import-error

from mhsg import parser
from mhsg.svFile import tokens

# mhsg.vhdlFile exports the class vhdlFile under the name of its module
vhdl = importlib.import_module("mhsg.vhdlFile.vhdlFile")

LANGUAGE = "systemverilog"

# Trivia that are kept as comments and whitespace
COMMENT_TRIVIA = ("LineComment", "BlockComment")
WHITESPACE_TRIVIA = ("Whitespace",)
END_OF_LINE_TRIVIA = ("EndOfLine",)
# Properties of syntax node classes that are not fields
# Fields of directives holding text that is not parsed as written: macro bodies and inactive `ifdef branches
UNPARSED_FIELDS = ("body", "disabledTokens")
NOT_FIELDS = {
    "kind",
    "parent",
    "sourceRange",
    "isList",
    "getFirstToken",
    "getLastToken",
    "to_json",
    "visit",
    "previousSibling",
    "nextSibling",
    "isEquivalentTo",
    "childNode",
    "childToken",
    "getChildCount",
}


class svFile(vhdl.vhdlFile):
    """A SystemVerilog or Verilog file: its tokens, with the methods of vhdlFile that work on any token list."""

    language = LANGUAGE

    def _processFile(self):
        # Lines come without their line ends from the command line, and with them from tests and the API
        lLines = [sLine.rstrip("\r\n") for sLine in self.filecontent]
        sText = "\n".join(lLines) + "\n" if lLines else ""
        self.syntax_tree = None
        self.lAllObjects = build_tokens(sText, self.filename or "source.sv")
        vhdl.set_code_tags(self.lAllObjects)
        self.oTokenMap = vhdl.process_tokens(self.lAllObjects)

    def get_lint_model(self):
        """SystemVerilog has no per-file lint model yet."""
        return None

    def set_indent_map(self, dIndentMap):
        """Indentation of SystemVerilog is not configured yet."""
        self.dIndentMap = dIndentMap

    def set_token_indent(self):
        """Indentation of SystemVerilog is not configured yet."""


def build_tokens(sText, sFileName):
    """Returns the mhsg tokens of a SystemVerilog text: lexed as written, classified from the syntax tree."""
    oSourceManager = pyslang.SourceManager()
    oTree = SyntaxTree.fromText(sText, oSourceManager, sFileName)
    oFirst = oTree.root.getFirstToken()
    dClasses = classify(oTree, oFirst.location.buffer.id) if oFirst is not None else {}
    oBuffer = oSourceManager.assignText(sFileName + " (as written)", sText)
    oLexer = Lexer(oBuffer, pyslang.BumpAllocator(), pyslang.Diagnostics(), oSourceManager, LexerOptions())
    lReturn = []
    while True:
        oToken = oLexer.lex()
        for oTrivia in oToken.trivia:
            add_trivia(lReturn, oTrivia.kind.name, oTrivia.getRawText())
        if oToken.kind == TokenKind.EndOfFile:
            break
        sKind = oToken.kind.name
        tClass = dClasses.get(oToken.location.offset)
        if tClass is None or tClass[2] != sKind:
            oClass = tokens.preprocessor if tokens.base_class(sKind) is tokens.preprocessor else tokens.unclassified
            oNew = oClass(oToken.rawText, sKind)
        else:
            tSyntax, sField = tClass[0], tClass[1]
            oNew = tokens.for_token(sKind, tSyntax, sField)(oToken.rawText, sKind, tSyntax, sField)
        add_text(lReturn, oNew)
    mark_blank_lines(lReturn)
    return lReturn


def add_trivia(lTokens, sKind, sText):
    """Adds whitespace, comments and line ends; other trivia, such as skipped text, are kept as unclassified text."""
    if sKind in END_OF_LINE_TRIVIA:
        lTokens.append(parser.carriage_return())
    elif sKind in WHITESPACE_TRIVIA:
        lTokens.append(whitespace(sText))
    elif sKind in COMMENT_TRIVIA:
        add_text(lTokens, parser.comment(sText))
    else:
        add_text(lTokens, tokens.unclassified(sText, sKind))


def add_text(lTokens, oToken):
    """Adds a token, split at line ends into one token per line, such as a block comment over several lines."""
    sText = oToken.get_value()
    if "\n" not in sText:
        mark_tab(oToken)
        lTokens.append(oToken)
        return
    lLines = sText.split("\n")
    for iLine, sLine in enumerate(lLines):
        if iLine > 0:
            lTokens.append(parser.carriage_return())
        sLine = sLine.rstrip("\r")
        sContent = sLine.lstrip(" \t")
        if iLine > 0 and len(sContent) < len(sLine):
            lTokens.append(whitespace(sLine[: len(sLine) - len(sContent)]))
            sLine = sContent
        if sLine:
            oPart = type(oToken).__new__(type(oToken))
            oPart.__dict__.update(oToken.__dict__)
            oPart.set_value(sLine)
            mark_tab(oPart)
            lTokens.append(oPart)


def whitespace(sText):
    oReturn = parser.whitespace(sText)
    mark_tab(oReturn)
    return oReturn


def mark_tab(oToken):
    """Flags whitespace and comments holding a tab, as the VHDL classifier does, for whitespace_002."""
    if isinstance(oToken, (parser.whitespace, parser.comment)) and "\t" in oToken.get_value():
        oToken.has_tab = True


def mark_blank_lines(lTokens):
    """Adds a blank_line token to each empty line, as for VHDL files."""
    lReturn = []
    bLineStart = True
    for oToken in lTokens:
        if isinstance(oToken, parser.carriage_return):
            if bLineStart:
                lReturn.append(parser.blank_line())
            bLineStart = True
        else:
            bLineStart = False
        lReturn.append(oToken)
    lTokens[:] = lReturn


_dFields = {}


def fields(oNode):
    """The names of the properties of a syntax node class that can hold tokens or nodes."""
    oClass = type(oNode)
    if oClass not in _dFields:
        lFields = []
        for sName in dir(oClass):
            if sName.startswith("_") or sName in NOT_FIELDS:
                continue
            oAttribute = getattr(oClass, sName, None)
            if not callable(oAttribute) or type(oAttribute).__name__ in ("property", "getset_descriptor", "nb_property"):
                lFields.append(sName)
        _dFields[oClass] = lFields
    return _dFields[oClass]


def classify(oTree, iBuffer):
    """Returns {offset: (syntax node kinds, field, token kind)} for the tokens of the file in a syntax tree."""
    dReturn = {}
    lStack = [(oTree.root, ())]
    while lStack:
        oNode, tPath = lStack.pop()
        tPath = tPath + (tokens.short_name(oNode.kind.name),)
        sUnparsed = set()
        for sField in UNPARSED_FIELDS:
            oValue = getattr(oNode, sField, None)
            if isinstance(oValue, list):
                sUnparsed.update(oToken.location.offset for oToken in oValue if isinstance(oToken, Token))
        dFields = {}
        for sField in fields(oNode):
            try:
                oValue = getattr(oNode, sField)
            except Exception:  # pylint: disable=broad-except
                continue
            if isinstance(oValue, Token) and oValue.location.buffer.id == iBuffer:
                dFields[oValue.location.offset] = sField
        for oChild in oNode:
            if oChild is None:
                continue
            if isinstance(oChild, Token):
                if oChild.location.buffer.id == iBuffer and oChild.location.offset not in sUnparsed:
                    dReturn[oChild.location.offset] = (tPath, dFields.get(oChild.location.offset), oChild.kind.name)
                for oTrivia in oChild.trivia:
                    oSyntax = oTrivia.syntax()
                    if oSyntax is not None:
                        # A directive stands on its own, whichever token it comes before
                        lStack.append((oSyntax, ()))
            elif isinstance(oChild, SyntaxNode):
                lStack.append((oChild, tPath))
    return dReturn
