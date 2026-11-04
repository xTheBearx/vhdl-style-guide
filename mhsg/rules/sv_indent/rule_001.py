# -*- coding: utf-8 -*-

import importlib

from mhsg import language, parser
from mhsg.rules.token_indent import token_indent as Rule
from mhsg.svFile import tokens

# mhsg.svFile exports the class svFile under the name of its module
svFile = importlib.import_module("mhsg.svFile.svFile")

lTokens = [tokens.token, parser.comment]


class rule_001(Rule):
    """
    This rule checks the indent of SystemVerilog and Verilog code.

    Each level is **indent_size** spaces, 4 by default. One level in are: the members of a module, package, interface
    or class; the items of a begin-end block, a function or a task; the ports and parameters of a declaration; the
    connections of an instance; the members of an enum or struct; the items of a case statement; and a statement
    under if, else, a loop, an always block or a case item when it is not a begin-end block.
    end, else, endmodule and the brackets closing a list are at the level of the construct they close.
    A comment is indented like the next line of code, or one level more above a line closing a construct. A comment
    line continuing the comment at the end of the line above, aligned with it, stays aligned with it.

    Continuation lines, such as the second line of a long expression, are checked by sv_indent_002; preprocessor
    directives are not checked,
    nor is a file with syntax errors, whose levels may be wrong near the errors, see sv_syntax_001.

    Two options follow other styles. **list_indent**, 1 by default, is the number of levels the ports and parameters
    of a declaration and the connections of an instance are indented; Verible's formatter indents them by its wrap
    width, which is 2 levels. **begin_style**, aligned by default, puts a begin on its own line under a control
    statement at the level of the statement; indented puts it one level in, with its items one level further.

    **Violation**

    .. code-block:: systemverilog

       module counter (
       input logic clk_i
       );
         always_ff @(posedge clk_i) begin
         count_q <= count_d;
           end
       endmodule

    **Fix**

    .. code-block:: systemverilog

       module counter (
           input logic clk_i
       );
           always_ff @(posedge clk_i) begin
               count_q <= count_d;
           end
       endmodule
    """

    def __init__(self):
        super().__init__(lTokens)
        self.languages = (language.SYSTEMVERILOG,)
        self.list_indent = 1
        self.configuration.append("list_indent")
        self.begin_style = "aligned"
        self.configuration.append("begin_style")

    def _get_tokens_of_interest(self, oFile):
        if getattr(oFile, "syntax_errors", None):
            return []
        set_style_levels(oFile, int(self.list_indent), str(self.begin_style).lower() == "indented")
        return super()._get_tokens_of_interest(oFile)

    def fix(self, oFile, dFixOnly=None):
        super().fix(oFile, dFixOnly)
        # A comment continuing a trailing comment moves with it
        if self.fixable and svFile.realign_comment_continuations(oFile.lAllObjects):
            oFile.update_token_map()


# The lists whose elements list_indent indents, by the kind of their node
INDENTED_LISTS = ("AnsiPortList", "NonAnsiPortList", "ParameterPortList", "HierarchicalInstance")
# The nodes a begin-end block is an item of, rather than the statement of a control statement
BLOCK_PARENTS = ("SequentialBlockStatement", "ParallelBlockStatement", "GenerateRegion", "GenerateBlock")


def set_style_levels(oFile, iListIndent, bIndentedBegin):
    """
    Adds to the levels of the tokens of a file what the options ask for: list_indent - 1 levels inside the brackets of
    port, parameter and connection lists, and with bIndentedBegin one level for a begin-end block whose begin starts
    a line under a control statement, the begin and end included. A comment takes the levels of the code around it.
    The level each token was given when the file was read is kept, so the levels are set again from it each time.
    """
    lRanges = []
    if iListIndent > 1:
        for oNode in oFile.nodes(*INDENTED_LISTS):
            oOpen, oClose = getattr(oNode, "openParen", None), getattr(oNode, "closeParen", None)
            if oOpen is not None and oClose is not None and oOpen.location.offset < oClose.location.offset:
                lRanges.append((oOpen.location.offset + 0.75, oClose.location.offset, iListIndent - 1))
    if bIndentedBegin:
        dIndexes = {getattr(o, "offset", None): i for i, o in enumerate(oFile.lAllObjects) if getattr(o, "offset", None) is not None}
        for oNode in oFile.nodes("SequentialBlockStatement"):
            oParent = oNode.parent
            if oParent is None or oParent.kind.name in BLOCK_PARENTS:
                continue
            oBegin, oEnd = oNode.getFirstToken(), oNode.getLastToken()
            iIndex = dIndexes.get(oBegin.location.offset)
            if iIndex is not None and starts_line(oFile.lAllObjects, iIndex):
                lRanges.append((oBegin.location.offset, oEnd.location.offset + 0.5, 1))
    fOffset = -1.0
    for oToken in oFile.lAllObjects:
        if getattr(oToken, "offset", None) is not None:
            fOffset = float(oToken.offset)
            fPosition = fOffset
        else:
            # A comment or other trivia is between the code token before it and the one after it
            fPosition = fOffset + 0.5
        if not hasattr(oToken, "base_indent"):
            if not hasattr(oToken, "get_indent"):
                continue
            oToken.base_indent = oToken.get_indent()
        if oToken.base_indent is None:
            continue
        iExtra = sum(iLevels for fStart, fEnd, iLevels in lRanges if fStart <= fPosition < fEnd)
        oToken.set_indent(oToken.base_indent + iExtra)


def starts_line(lTokens, iIndex):
    """True if only whitespace is between the token at iIndex and the start of its line."""
    for oToken in reversed(lTokens[:iIndex]):
        if isinstance(oToken, parser.carriage_return):
            return True
        if not isinstance(oToken, parser.whitespace):
            return False
    return True
