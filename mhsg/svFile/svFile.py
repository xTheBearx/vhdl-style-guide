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

import bisect
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

from mhsg import parser, token_map
from mhsg.svFile import indent, lint, tokens

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
        self.parse("\n".join(lLines) + "\n" if lLines else "")

    def parse(self, sText):
        """Builds the tokens of a text, with its syntax tree and the syntax nodes by kind."""
        # The source manager is kept with the tree, which refers to its buffers
        self.lAllObjects, (self.syntax_tree, self.source_manager), self.dNodes = build_tokens(sText, self.filename or "source.sv", bTree=True)
        self.dTokenAtOffset = {o.offset: o for o in self.lAllObjects if getattr(o, "offset", None) is not None}
        self.syntax_errors = syntax_errors(self.syntax_tree)
        self.lint_model = None
        vhdl.set_code_tags(self.lAllObjects)
        self.oTokenMap = self.build_token_map()

    def reparse(self):
        """
        Parses the file again as it is now, after a fix that changed its structure, so the classes, indent levels
        and syntax tree of the tokens describe the fixed code.
        """
        self.parse("\n".join(self.get_lines()[1:]) + "\n")

    def nodes(self, *lKinds):
        """The syntax nodes of the given kinds, such as AlwaysFFBlock, in the file."""
        lReturn = []
        for sKind in lKinds:
            lReturn.extend(self.dNodes.get(sKind, []))
        return lReturn

    def token_at_or_after(self, iOffset):
        """The first token of the file at or after an offset, or None."""
        lOffsets = sorted(self.dTokenAtOffset)
        iIndex = bisect.bisect_left(lOffsets, iOffset)
        return self.dTokenAtOffset[lOffsets[iIndex]] if iIndex < len(lOffsets) else None

    def token_at(self, oSyntaxToken):
        """The mhsg token for a token of the syntax tree, or None for one not in the file as written."""
        if oSyntaxToken is None:
            return None
        return self.dTokenAtOffset.get(oSyntaxToken.location.offset)

    def build_token_map(self):
        """The token map, where each token is also found under the base classes of its class, such as keyword."""
        return build_token_map(self.lAllObjects)

    def get_lint_model(self):
        """The lint model of the file as it is now, made the first time a lint rule asks for it."""
        if self.lint_model is None:
            self.lint_model = lint.LintModel(self.syntax_tree)
        return self.lint_model

    def set_indent_map(self, dIndentMap):
        """Indentation of SystemVerilog is not configured yet."""
        self.dIndentMap = dIndentMap

    def set_token_indent(self):
        """Indentation of SystemVerilog is not configured yet."""


# Diagnostics of a file checked on its own, without its include files and the defines of other files: they do not
# make the syntax tree wrong where the rules look
PREPROCESSOR_DIAGNOSTICS = {"UnknownDirective", "CouldNotOpenIncludeFile", "UndefinedMacro", "UnknownDiagPragma"}
# Diagnostics of style that sv_label_001 reports and fixes; the syntax tree is complete
STYLE_DIAGNOSTICS = {"EndNameMismatch", "EndNameNotEmpty"}


def node_offset(oNode):
    oFirst = oNode.getFirstToken()
    return oFirst.location.offset if oFirst is not None else -1


def syntax_errors(oTree):
    """The syntax errors of a tree as (offset, name of the error), leaving out those of the preprocessor."""
    lReturn = []
    for oDiagnostic in oTree.diagnostics:
        sName = str(oDiagnostic.code).replace("DiagCode(", "").rstrip(")")
        if oDiagnostic.isError() and sName not in PREPROCESSOR_DIAGNOSTICS | STYLE_DIAGNOSTICS:
            lReturn.append((oDiagnostic.location.offset, sName))
    return lReturn


def build_tokens(sText, sFileName, bTree=False):
    """
    Returns the mhsg tokens of a SystemVerilog text: lexed as written, classified from the syntax tree. With bTree,
    returns (tokens, (syntax tree, its source manager), {kind: syntax nodes}).
    """
    oSourceManager = pyslang.SourceManager()
    oTree = SyntaxTree.fromText(sText, oSourceManager, sFileName)
    oFirst = oTree.root.getFirstToken()
    dNodes = {}
    dClasses = classify(oTree, oFirst.location.buffer.id, line_starts(sText), dNodes) if oFirst is not None else {}
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
        oInfo = dClasses.get(oToken.location.offset)
        if oInfo is None or oInfo.kind != sKind:
            oClass = tokens.preprocessor if tokens.base_class(sKind) is tokens.preprocessor else tokens.unclassified
            oNew = oClass(oToken.rawText, sKind)
        else:
            oNew = tokens.for_token(sKind, oInfo.syntax, oInfo.field)(oToken.rawText, sKind, oInfo.syntax, oInfo.field)
            oNew.set_indent(oInfo.indent)
            oNew.closing = oInfo.closing
        # The offset of the token in the text, by which rules find it from the syntax tree
        oNew.offset = oToken.location.offset
        add_text(lReturn, oNew)
    mark_blank_lines(lReturn)
    set_comment_indents(lReturn)
    # The nodes of each kind in the order of the file
    for lNodes in dNodes.values():
        lNodes.sort(key=node_offset)
    if bTree:
        return lReturn, (oTree, oSourceManager), dNodes
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
            # The lines of a block comment after its first keep their own layout
            oPart.continued = iLine > 0
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


class token_info:
    """What the syntax tree tells about a token of the file."""

    __slots__ = ("syntax", "field", "kind", "indent", "closing")

    def __init__(self, tSyntax, sField, sKind, iIndent, bClosing):
        # The syntax node kinds from the root down to the node holding the token
        self.syntax = tSyntax
        # The field of that node holding the token, or None for an element of a list
        self.field = sField
        self.kind = sKind
        # The indent level of the token when it starts a line, or None when indentation does not apply to it
        self.indent = iIndent
        # True for a token that closes a construct, such as end or a closing parenthesis
        self.closing = bClosing


def line_starts(sText):
    """
    The offsets of the first character, other than spaces and tabs, of each line. slang's offsets count bytes of
    UTF-8, so these do too.
    """
    sReturn = set()
    iStart = 0
    for bLine in sText.encode("utf-8").split(b"\n"):
        bContent = bLine.lstrip(b" \t")
        if bContent:
            sReturn.add(iStart + len(bLine) - len(bContent))
        iStart += len(bLine) + 1
    return sReturn


def classify(oTree, iBuffer, sLineStarts, dNodes=None):
    """
    Returns {offset: token_info} for the tokens of the file in a syntax tree; sLineStarts are the offsets of the
    tokens that start a line.
    """
    dReturn = {}
    # The indent levels of the tokens that start an item, such as a statement or a port: {offset: level}
    dItemStarts = {}
    lStack = [(oTree.root, (), 0)]
    # The offsets of the tokens in the arguments of macro uses
    sMacroArguments = set()
    first_offset = _first_offset_function(iBuffer)
    iRoot = first_offset(oTree.root)
    if iRoot is not None:
        dItemStarts[iRoot] = 0
    while lStack:
        oNode, tPath, iLevel = lStack.pop()
        sKind = oNode.kind.name
        if dNodes is not None:
            dNodes.setdefault(sKind, []).append(oNode)
        tPath = tPath + (tokens.short_name(sKind),)
        dFields, sUnparsed, dListStarts = node_fields(oNode)
        # A list whose first element is on the line of its opening bracket is aligned rather than indented, such as
        # the arguments of a call continued under the first; its elements are not checked
        sAligned = {sField for sField, iOffset in dListStarts.items() if iOffset is not None and iOffset not in sLineStarts}
        lFieldsOfNode = [(sField, bList) for sField, bList in dFields.values()]
        # An empty list, such as the items of an empty begin-end block, still makes a body
        lFieldsOfNode.extend((sField, True) for sField in dListStarts if dListStarts[sField] is None)
        bHasBody = any(indent.is_body_field(sKind, sField, bList) and sField not in sAligned for sField, bList in lFieldsOfNode)
        for oChild in oNode:
            if oChild is None:
                continue
            if isinstance(oChild, Token):
                iOffset = oChild.location.offset
                # Zero-width tokens, such as the placeholder of an implicit type, share the offset of the next token
                if oChild.location.buffer.id == iBuffer and iOffset not in sUnparsed and oChild.rawText:
                    sField, _ = dFields.get(("T", iOffset), (None, False))
                    sChildKind = oChild.kind.name
                    iIndent = dItemStarts.get(iOffset)
                    bClosing = bHasBody and indent.is_closing(sChildKind)
                    if iIndent is None and iLevel is not None and bHasBody and indent.is_own_line(sChildKind):
                        iIndent = iLevel
                    dReturn[iOffset] = token_info(tPath, sField, sChildKind, iIndent, bClosing)
                for oTrivia in oChild.trivia:
                    oSyntax = oTrivia.syntax()
                    if oSyntax is not None and oSyntax.kind.name == "MacroUsage" and oSyntax.args is not None:
                        # The arguments of a macro use are text the macro places; rules leave them alone
                        sMacroArguments.update(token_offsets(oSyntax.args, iBuffer))
                    if oSyntax is not None:
                        # A directive stands on its own, whichever token it comes before; it is not indented yet
                        lStack.append((oSyntax, (), None))
            elif isinstance(oChild, SyntaxNode):
                iChildLevel = None
                if iLevel is not None:
                    iOffset = first_offset(oChild)
                    sField, bList = dFields.get(("N", oChild.kind.name, iOffset), (None, False))
                    iIncrement = indent.increment(sKind, sField, bList, oChild.kind.name)
                    if bList and sField in sAligned:
                        # Aligned elements keep the level of their list and are not checked
                        iIncrement = None
                    iChildLevel = iLevel + (iIncrement or 0)
                    if iIncrement is not None and iOffset is not None:
                        dItemStarts.setdefault(iOffset, iChildLevel)
                    if indent.is_expression(oChild.kind.name):
                        # Inside an expression, lines are continuations, which are not checked
                        iChildLevel = None
                lStack.append((oChild, tPath, iChildLevel))
    for iOffset in sMacroArguments:
        dReturn.pop(iOffset, None)
    return dReturn


def token_offsets(oNode, iBuffer):
    """The offsets of all tokens under a syntax node, in the file's buffer."""
    sReturn = set()
    lStack = [oNode]
    while lStack:
        oItem = lStack.pop()
        for oChild in oItem:
            if isinstance(oChild, Token):
                if oChild.location.buffer.id == iBuffer:
                    sReturn.add(oChild.location.offset)
            elif isinstance(oChild, SyntaxNode):
                lStack.append(oChild)
    return sReturn


def _first_offset_function(iBuffer):
    def first_offset(oNode):
        oToken = oNode.getFirstToken()
        if oToken is None or oToken.location.buffer.id != iBuffer:
            return None
        return oToken.location.offset

    return first_offset


def node_fields(oNode):
    """
    Returns ({key: (field, in a list)}, unparsed offsets) for the children of a syntax node, where the key of a token
    is ("T", offset) and that of a node ("N", kind, offset of its first token).
    """
    dReturn = {}
    sUnparsed = set()
    # The offset of the first element of each list
    dListStarts = {}
    for sField in fields(oNode):
        try:
            oValue = getattr(oNode, sField)
        except Exception:  # pylint: disable=broad-except
            continue
        if isinstance(oValue, Token):
            dReturn[("T", oValue.location.offset)] = (sField, False)
        elif isinstance(oValue, SyntaxNode):
            add_field(dReturn, oValue, sField, False)
        elif isinstance(oValue, list):
            # pyslang gives lists, such as the members of a module, as Python lists
            if sField in UNPARSED_FIELDS:
                sUnparsed.update(oToken.location.offset for oToken in oValue if isinstance(oToken, Token))
            else:
                dListStarts.setdefault(sField, None)
                for oElement in oValue:
                    iOffset = add_field(dReturn, oElement, sField, True)
                    if iOffset is not None and dListStarts[sField] is None:
                        dListStarts[sField] = iOffset
    return dReturn, sUnparsed, dListStarts


def add_field(dFields, oChild, sField, bList):
    """Records the field of a child; returns the offset of the child's first token, or None."""
    if isinstance(oChild, Token):
        dFields[("T", oChild.location.offset)] = (sField, bList)
        return oChild.location.offset
    if isinstance(oChild, SyntaxNode):
        oFirst = oChild.getFirstToken()
        if oFirst is not None:
            dFields[("N", oChild.kind.name, oFirst.location.offset)] = (sField, bList)
            return oFirst.location.offset
    return None


def set_comment_indents(lTokens):
    """
    Gives a comment that starts a line the indent of the next line of code: one level more when that line closes a
    construct, as a comment above end belongs to the statements before it.
    """
    lPending = []
    bLineStart = True
    iColumn = 0
    # The column of the comment ending the previous line, if it ended with one, and that of the current line
    iTrailingComment = None
    iThisTrailingComment = None
    oTrailingComment = None
    oThisTrailingComment = None
    for oToken in lTokens:
        if isinstance(oToken, (parser.carriage_return, parser.blank_line)):
            if isinstance(oToken, parser.carriage_return):
                iTrailingComment = iThisTrailingComment
                oTrailingComment = oThisTrailingComment
                iThisTrailingComment = None
                oThisTrailingComment = None
                iColumn = 0
            bLineStart = True
            continue
        iTokenColumn = iColumn
        iColumn += len(oToken.get_value())
        if isinstance(oToken, parser.whitespace):
            continue
        if isinstance(oToken, parser.comment) and not bLineStart:
            # A comment after code on its line
            iThisTrailingComment = iTokenColumn
            oThisTrailingComment = oToken
        if bLineStart:
            if isinstance(oToken, parser.comment):
                if getattr(oToken, "continued", False):
                    pass
                elif iTokenColumn == iTrailingComment and iTokenColumn > 0:
                    # A comment continuing the comment at the end of the line above, aligned with it; it follows
                    # that comment when the line above is indented again, see realign_comment_continuations
                    iThisTrailingComment = iTokenColumn
                    oThisTrailingComment = oToken
                    oToken.continues = oTrailingComment
                else:
                    lPending.append(oToken)
            else:
                iIndent = oToken.get_indent()
                if iIndent is not None and getattr(oToken, "closing", False):
                    iIndent += 1
                for oComment in lPending:
                    oComment.set_indent(iIndent)
                lPending = []
        bLineStart = False


def realign_comment_continuations(lTokens):
    """
    Moves each comment continuing a trailing comment, see set_comment_indents, back under the comment it continues,
    after the indent of the line above was fixed. Returns True if any token changed.
    """
    bChanged = False
    dColumns = {}
    iColumn = 0
    iToken = 0
    while iToken < len(lTokens):
        oToken = lTokens[iToken]
        if isinstance(oToken, parser.carriage_return):
            iColumn = 0
            iToken += 1
            continue
        oAnchor = getattr(oToken, "continues", None)
        if oAnchor is not None and id(oAnchor) in dColumns and not oToken.has_code_tag("sv_indent_001"):
            iTarget = dColumns[id(oAnchor)]
            oPrevious = lTokens[iToken - 1] if iToken > 0 else None
            if isinstance(oPrevious, parser.whitespace):
                if oPrevious.get_value() != " " * iTarget:
                    oPrevious.set_value(" " * iTarget)
                    oPrevious.has_tab = False
                    bChanged = True
                iColumn = iTarget
            elif iTarget > 0:
                lTokens.insert(iToken, parser.whitespace(" " * iTarget))
                bChanged = True
                iColumn = iTarget
                iToken += 1
        if isinstance(oToken, parser.comment):
            dColumns[id(oToken)] = iColumn
        iColumn += len(oToken.get_value())
        iToken += 1
    return bChanged


def build_token_map(lTokens):
    """Returns the token map, with each SystemVerilog token also under the base classes of its class."""
    oTokenMap = vhdl.process_tokens(lTokens)
    dMap = oTokenMap.dMap
    sChanged = set()
    for iToken, oToken in enumerate(lTokens):
        if not isinstance(oToken, tokens.token):
            continue
        for oClass in tokens.token_classes(type(oToken))[1:]:
            sBase, sSub = token_map.extract_unique_id(oClass)
            dMap.setdefault(sBase, {}).setdefault(sSub, []).append(iToken)
            sChanged.add((sBase, sSub))
    for sBase, sSub in sChanged:
        dMap[sBase][sSub].sort()
    return oTokenMap
