# -*- coding: utf-8 -*-
"""
SystemVerilog and Verilog files, read with slang (pyslang).

The tokens come from slang's lexer run on the text as written, before preprocessing, so the file is kept exactly,
with its macro uses, directives and inactive `ifdef branches. Each token is then looked up in slang's syntax tree by
its offset, which tells the syntax node and field it belongs to. The code of inactive `ifdef branches is classified
from parses with the macros of their conditions switched, and marked inactive; the arguments of macro uses where the
macro places them, marked macro_argument; and the bodies of macro definitions where the first use of each macro places
them, marked macro_body. Tokens no parse places, such as the bodies of macros never used, are unclassified.

svFile shares the methods of vhdlFile that work on the list of tokens, such as get_tokens_matching and get_lines,
so the fix pipeline and the rules that only look at whitespace, comments and lines work unchanged. Rules declare the
languages they apply to, see rule.Rule.languages.
"""

import bisect
import importlib
import os
import re

import pyslang

# The submodules of pyslang are made when its extension loads, so pylint cannot find them
from pyslang.parsing import (  # pylint: disable=import-error
    Lexer,
    LexerOptions,
    PreprocessorOptions,
    Token,
    TokenKind,
)
from pyslang.syntax import SyntaxNode, SyntaxTree  # pylint: disable=import-error

from mhsg import language, parser, token_map
from mhsg.svFile import indent, lint, preprocessor, project, tokens

# mhsg.vhdlFile exports the class vhdlFile under the name of its module
vhdl = importlib.import_module("mhsg.vhdlFile.vhdlFile")

LANGUAGE = language.SYSTEMVERILOG

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
    """
    A SystemVerilog or Verilog file: its tokens, with the methods of vhdlFile that work on any token list. Its language
    is verilog for a .v or .vh file, unless v_files in the configuration says systemverilog, and systemverilog
    otherwise, see language.py.
    """

    language = LANGUAGE

    def _processFile(self):
        sLanguageName = language.of_file(self.filename, getattr(self.configuration, "dConfig", None))
        self.language = sLanguageName if sLanguageName in language.VERILOG_LANGUAGES else LANGUAGE
        # Lines come without their line ends from the command line, and with them from tests and the API
        lLines = [sLine.rstrip("\r\n") for sLine in self.filecontent]
        self.parse("\n".join(lLines) + "\n" if lLines else "")

    def preprocessor_options(self):
        """The pyslang options the file is parsed with: the preprocessor settings and the version of its language."""
        return preprocessor.options(getattr(self.configuration, "dConfig", None), self.language)

    def parse(self, sText):
        """Builds the tokens of a text, with its syntax tree and the syntax nodes by kind."""
        # The offset of the start of each line, in bytes as slang counts, see line_of
        self.line_offsets = [0]
        for iIndex, iByte in enumerate(sText.encode("utf-8")):
            if iByte == 10:
                self.line_offsets.append(iIndex + 1)
        # The source manager is kept with the tree, which refers to its buffers
        oOptions = self.preprocessor_options()
        sPath = os.path.abspath(self.filename) if self.filename and self.filename != "stdin" else ""
        self.text = sText
        self.lAllObjects, (self.syntax_tree, self.source_manager, self.buffer_id), self.dNodes = build_tokens(
            sText,
            self.filename or "source.sv",
            bTree=True,
            oOptions=oOptions,
            sPath=sPath,
        )
        self.iVersion = getattr(self, "iVersion", 0) + 1
        self.dTokenAtOffset = {o.offset: o for o in self.lAllObjects if getattr(o, "offset", None) is not None}
        self.syntax_errors = syntax_errors(self.syntax_tree)
        mark_error_units(self.lAllObjects, error_spans(self.syntax_tree, self.buffer_id, self.line_offsets))
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

    def line_of(self, iOffset):
        """The line number, from 1, of an offset in the text."""
        return bisect.bisect_right(self.line_offsets, iOffset)

    def token_at_or_after(self, iOffset):
        """The first token of the file at or after an offset, or None."""
        lOffsets = sorted(self.dTokenAtOffset)
        iIndex = bisect.bisect_left(lOffsets, iOffset)
        return self.dTokenAtOffset[lOffsets[iIndex]] if iIndex < len(lOffsets) else None

    def token_at(self, oSyntaxToken):
        """The mhsg token for a token of the syntax tree, or None for one not in the file as written."""
        if oSyntaxToken is None or oSyntaxToken.location.buffer.id != self.buffer_id:
            return None
        return self.dTokenAtOffset.get(oSyntaxToken.location.offset)

    def build_token_map(self):
        """The token map, where each token is also found under the base classes of its class, such as keyword."""
        return build_token_map(self.lAllObjects)

    def get_lint_model(self):
        """The lint model of the file as it is now, made the first time a lint rule asks for it."""
        if self.lint_model is None:
            # The warnings of the whole run, when the run compiled this file as it is now, see project.py
            dProject = getattr(self.configuration, "sv_lint_project", None) or {}
            dEntry = dProject.get(os.path.abspath(self.filename)) if self.filename else None
            if dEntry is not None and dEntry["hash"] == project.text_hash("\n".join(self.get_lines()[1:]) + "\n"):
                self.lint_model = lint.LintModel.from_project(dEntry)
            else:
                self.lint_model = lint.LintModel(self.syntax_tree, self.buffer_id)
            self.add_inactive_warnings(self.lint_model)
        return self.lint_model

    def add_inactive_warnings(self, oModel):
        """
        Adds to a lint model the warnings in the code of inactive `ifdef branches: from the file linted on its own with
        each macro of its conditions switched, see switched_trees.
        """
        setInactive = {o.offset for o in self.lAllObjects if getattr(o, "inactive", False) and getattr(o, "offset", None) is not None}
        if not setInactive:
            return
        sPath = os.path.abspath(self.filename) if self.filename and self.filename != "stdin" else ""
        sText = "\n".join(self.get_lines()[1:]) + "\n"
        setSeen = {(o.offset, o.name) for o in oModel.diagnostics}
        for oTree, iBuffer in switched_trees(sText, sPath or self.filename or "source.sv", self.preprocessor_options()):
            for oDiagnostic in lint.LintModel(oTree, iBuffer).diagnostics:
                tKey = (oDiagnostic.offset, oDiagnostic.name)
                # The first token at or after the offset of a warning is the one it is reported at
                oToken = self.token_at_or_after(oDiagnostic.offset)
                if tKey in setSeen or oToken is None or oToken.offset not in setInactive:
                    continue
                setSeen.add(tKey)
                oModel.diagnostics.append(oDiagnostic)
        oModel.diagnostics.sort(key=lambda o: o.offset)

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


def error_spans(oTree, iBuffer, lLineOffsets):
    """
    The (first, last) offsets of the parts of a file slang may have parsed wrongly. slang parses the code before an
    error as written, and starts again at the next item of a design unit, such as a declaration or an always block, or
    at the next unit: so for an error in an item, from the line of the error to the end of the item; for an error in
    a unit outside its items, such as in its header, from that line to the end of the unit; for an error outside the
    units, from that line to the next unit. An error in an included file makes the whole file such a part.
    """
    lErrors = []
    for oDiagnostic in oTree.diagnostics:
        sName = str(oDiagnostic.code).replace("DiagCode(", "").rstrip(")")
        if not oDiagnostic.isError() or sName in PREPROCESSOR_DIAGNOSTICS | STYLE_DIAGNOSTICS:
            continue
        if oDiagnostic.location.buffer.id != iBuffer:
            return [(0, float("inf"))]
        lErrors.append(oDiagnostic.location.offset)
    if not lErrors:
        return []
    lUnits = []
    for oMember in getattr(oTree.root, "members", None) or []:
        tUnit = node_span(oMember, iBuffer)
        if tUnit is not None:
            lItems = [t for t in (node_span(o, iBuffer) for o in getattr(oMember, "members", None) or []) if t is not None]
            lUnits.append((tUnit, lItems))
    lReturn = []
    for iError in sorted(lErrors):
        iLine = lLineOffsets[bisect.bisect_right(lLineOffsets, iError) - 1] if lLineOffsets else 0
        tUnit = next((t for t in lUnits if t[0][0] <= iError <= t[0][1]), None)
        if tUnit is None:
            iEnd = min((t[0][0] for t in lUnits if t[0][0] > iError), default=float("inf"))
        else:
            tItem = next(((a, b) for a, b in tUnit[1] if a <= iError <= b), None)
            iEnd = tItem[1] if tItem is not None else tUnit[0][1]
        lReturn.append((iLine, iEnd))
    return lReturn


def node_span(oNode, iBuffer):
    """The (first, last) offsets of a syntax node in the file, or None for one not all in it."""
    oFirst = oNode.getFirstToken()
    oLast = oNode.getLastToken()
    if oFirst is None or oLast is None or oFirst.location.buffer.id != iBuffer or oLast.location.buffer.id != iBuffer:
        return None
    return oFirst.location.offset, oLast.location.offset + len(oLast.rawText)


def mark_error_units(lTokens, lSpans):
    """Marks in_error the tokens of the parts of a file that slang may have parsed wrongly, see error_spans."""
    if not lSpans:
        return
    lOffsets = [(i, o.offset) for i, o in enumerate(lTokens) if getattr(o, "offset", None) is not None]
    for iFirst, iLast in lSpans:
        lInside = [i for i, iOffset in lOffsets if iFirst <= iOffset <= iLast]
        if not lInside:
            continue
        # The whitespace and comments between the tokens of the part are in it too
        for oToken in lTokens[lInside[0] : lInside[-1] + 1]:
            oToken.in_error = True


def in_buffer(oNode, iBuffer):
    """True for a node of the file, False for one of a file it includes; a node without tokens counts as the file's."""
    oFirst = oNode.getFirstToken()
    return oFirst is None or oFirst.location.buffer.id == iBuffer


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


def build_tokens(sText, sFileName, bTree=False, oOptions=None, sPath=""):
    """
    Returns the mhsg tokens of a SystemVerilog or Verilog text: lexed as written, classified from the syntax tree. With bTree,
    returns (tokens, (syntax tree, its source manager, the id of the file's buffer), {kind: syntax nodes}), where the
    nodes are those of the file, not of the files it includes.
    """
    oSourceManager = pyslang.SourceManager()
    # The buffer is named by the path of the file, so includes are found next to it; the options carry the defines
    # and include directories. With includes, the tree also holds the tokens of other buffers.
    oFileBuffer = oSourceManager.assignText(sPath or sFileName, sText)
    oTree = SyntaxTree.fromBuffer(oFileBuffer, oSourceManager, oOptions) if oOptions is not None else SyntaxTree.fromBuffer(oFileBuffer, oSourceManager)
    dNodes = {}
    sDisabled = set()
    dClasses = classify(oTree, oFileBuffer.id.id, line_starts(sText), dNodes, oSourceManager, sDisabled)
    # The code of inactive `ifdef branches is not in the tree: the parses with each macro its conditions test switched
    # give its indent levels
    dInactive = inactive_levels(sText, sPath or sFileName, oOptions, dClasses, sDisabled)
    oBuffer = oSourceManager.assignText(sFileName + " (as written)", sText)
    # The lexer reads the keywords of the language of the file, as the parser does: logic is a name in Verilog
    oLexerOptions = LexerOptions()
    if preprocessor.language_version(oOptions) is not None:
        oLexerOptions.languageVersion = preprocessor.language_version(oOptions)
    oLexer = Lexer(oBuffer, pyslang.BumpAllocator(), pyslang.Diagnostics(), oSourceManager, oLexerOptions)
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
            oAlternate = dInactive.get(oToken.location.offset)
            if oClass is tokens.unclassified and oAlternate is not None and oAlternate.kind == sKind:
                # Code of an inactive branch takes the class and level it has where the branch is active, so the rules
                # check it as other code; rules that read the syntax tree do not see it, as it is not in the tree
                oNew = tokens.for_token(sKind, oAlternate.syntax, oAlternate.field)(oToken.rawText, sKind, oAlternate.syntax, oAlternate.field)
                oNew.set_indent(oAlternate.indent)
                oNew.closing = oAlternate.closing
                oNew.inactive = True
        else:
            oNew = tokens.for_token(sKind, oInfo.syntax, oInfo.field)(oToken.rawText, sKind, oInfo.syntax, oInfo.field)
            oNew.set_indent(oInfo.indent)
            oNew.closing = oInfo.closing
            if oInfo.argument:
                oNew.macro_argument = True
            if oInfo.body:
                oNew.macro_body = True
        # The offset of the token in the text, by which rules find it from the syntax tree
        oNew.offset = oToken.location.offset
        add_text(lReturn, oNew)
    mark_blank_lines(lReturn)
    set_comment_indents(lReturn)
    # The nodes of each kind in the order of the file
    for lNodes in dNodes.values():
        lNodes.sort(key=node_offset)
    if bTree:
        return lReturn, (oTree, oSourceManager, oFileBuffer.id.id), dNodes
    return lReturn


# The conditions of `ifdef branches, and the most parses made to find the levels of the code of inactive branches
reCondition = re.compile(r"`(?:ifdef|ifndef|elsif)\s+([A-Za-z_][A-Za-z0-9_$]*)")
MAX_ALTERNATE_PARSES = 8


def switched_trees(sText, sPath, oOptions):
    """
    Yields (syntax tree, buffer id) of the parses of a text with a macro of its `ifdef conditions switched: defined when
    it is not, undefined when it is. One parse for each macro, at most MAX_ALTERNATE_PARSES.
    """
    lMacros = list(dict.fromkeys(reCondition.findall(sText)))[:MAX_ALTERNATE_PARSES]
    oBase = getattr(oOptions, "preprocessorOptions", None) if oOptions is not None else None
    lDefines = list(oBase.predefines) if oBase is not None else []
    lIncludes = list(oBase.additionalIncludePaths) if oBase is not None else []
    for sMacro in lMacros:
        bDefined = any(s.split("=")[0] == sMacro for s in lDefines)
        oSwitched = PreprocessorOptions()
        oSwitched.predefines = [s for s in lDefines if s.split("=")[0] != sMacro] + ([] if bDefined else [sMacro])
        oSwitched.undefines = [sMacro] if bDefined else []
        oSwitched.additionalIncludePaths = lIncludes
        if oBase is not None:
            oSwitched.languageVersion = oBase.languageVersion
        oManager = pyslang.SourceManager()
        oBuffer = oManager.assignText(sPath, sText)
        try:
            oTree = SyntaxTree.fromBuffer(oBuffer, oManager, pyslang.Bag([oSwitched]))
        except (RuntimeError, ValueError):
            continue
        yield oTree, oBuffer.id.id


def inactive_levels(sText, sPath, oOptions, dClasses, sDisabled=None):
    """
    Returns {offset: token_info} for the tokens that only the parses with a macro of the `ifdef conditions of a text
    switched have, see switched_trees; the first parse that has a token gives its level.
    """
    dReturn = {}
    if sDisabled is not None and not sDisabled:
        # No inactive branch: nothing for the other parses to classify
        return dReturn
    lWanted = sorted(sDisabled) if sDisabled is not None else None
    sStarts = line_starts(sText)
    for oTree, iBuffer in switched_trees(sText, sPath, oOptions):
        for iOffset, oInfo in classify(oTree, iBuffer, sStarts, lWanted=lWanted).items():
            if iOffset not in dClasses and iOffset not in dReturn:
                dReturn[iOffset] = oInfo
    return dReturn


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

    __slots__ = ("syntax", "field", "kind", "indent", "closing", "argument", "body")

    def __init__(self, tSyntax, sField, sKind, iIndent, bClosing, bArgument=False, bBody=False):
        # The syntax node kinds from the root down to the node holding the token
        self.syntax = tSyntax
        # The field of that node holding the token, or None for an element of a list
        self.field = sField
        self.kind = sKind
        # The indent level of the token when it starts a line, or None when indentation does not apply to it
        self.indent = iIndent
        # True for a token that closes a construct, such as end or a closing parenthesis
        self.closing = bClosing
        # True for a token in the arguments of a macro use, classified where the macro places it
        self.argument = bArgument
        # True for a token in the body of a macro definition, classified where a use of the macro places it
        self.body = bBody


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


def classify(oTree, iBuffer, sLineStarts, dNodes=None, oSourceManager=None, sDisabled=None, lWanted=None):
    """
    Returns {offset: token_info} for the tokens of the file in a syntax tree; sLineStarts are the offsets of the
    tokens that start a line. With the source manager, the tokens of the arguments of macro uses are classified where
    the macro places them, the first place for an argument placed more than once, without an indent level.
    sDisabled, a set, gets the offsets of the tokens of inactive `ifdef branches. With lWanted, sorted offsets, only
    the nodes that hold one of them are classified, which saves time in the parses of inactive branches.
    """
    dReturn = {}
    # The indent levels of the tokens that start an item, such as a statement or a port: {offset: level}
    dItemStarts = {}
    lStack = [(oTree.root, (), 0)]
    # The offsets of the tokens in the arguments of macro uses, and what they are where the macros place them; and the
    # tokens of the bodies of macro definitions where the first use of each places them
    sMacroArguments = set()
    dArguments = {}
    dBodies = {}
    first_offset = _first_offset_function(iBuffer)
    iRoot = first_offset(oTree.root)
    if iRoot is not None:
        dItemStarts[iRoot] = 0
    while lStack:
        oNode, tPath, iLevel = lStack.pop()
        sKind = oNode.kind.name
        if sDisabled is not None and getattr(oNode, "disabledTokens", None):
            sDisabled.update(o.location.offset for o in oNode.disabledTokens if isinstance(o, Token) and o.location.buffer.id == iBuffer)
        if dNodes is not None and in_buffer(oNode, iBuffer):
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
                elif oSourceManager is not None and oChild.rawText and oSourceManager.isMacroLoc(oChild.location):
                    bArgument = oSourceManager.isMacroArgLoc(oChild.location)
                    oOriginal = oSourceManager.getFullyOriginalLoc(oChild.location)
                    dTarget = dArguments if bArgument else dBodies
                    if oOriginal.buffer.id == iBuffer and oOriginal.offset not in dTarget:
                        sField, _ = dFields.get(("T", iOffset), (None, False))
                        dTarget[oOriginal.offset] = token_info(tPath, sField, oChild.kind.name, None, False, bArgument, not bArgument)
                for oTrivia in oChild.trivia:
                    oSyntax = oTrivia.syntax()
                    if oSyntax is not None and oSyntax.kind.name == "MacroUsage" and oSyntax.args is not None:
                        # The arguments of a macro use are text the macro places: classified where it places them
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
                if lWanted is not None and not holds_wanted(oChild, iBuffer, lWanted):
                    continue
                lStack.append((oChild, tPath, iChildLevel))
    for iOffset in sMacroArguments:
        dReturn.pop(iOffset, None)
        if iOffset in dArguments:
            dReturn[iOffset] = dArguments[iOffset]
    for iOffset, oInfo in dBodies.items():
        dReturn.setdefault(iOffset, oInfo)
    return dReturn


def holds_wanted(oNode, iBuffer, lWanted):
    """Whether a node holds one of the sorted offsets of lWanted, or may: True when its tokens are not all in the file."""
    oFirst = oNode.getFirstToken()
    oLast = oNode.getLastToken()
    if oFirst is None or oLast is None or oFirst.location.buffer.id != iBuffer or oLast.location.buffer.id != iBuffer:
        return True
    iIndex = bisect.bisect_left(lWanted, oFirst.location.offset)
    return iIndex < len(lWanted) and lWanted[iIndex] <= oLast.location.offset


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
