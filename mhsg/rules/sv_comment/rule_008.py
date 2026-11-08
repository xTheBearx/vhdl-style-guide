# -*- coding: utf-8 -*-

import re

from pyslang.syntax import SyntaxTree  # pylint: disable=import-error

from mhsg import language, parser, violation
from mhsg.rule_group import structure

KEYWORDS = frozenset(
    """
    always always_comb always_ff always_latch and assign automatic begin bit byte case casex casez default defparam
    else end endcase endfunction endgenerate endmodule endpackage endtask enum for forever function generate genvar if
    import initial inout input int integer localparam logic module negedge not or output package packed parameter
    posedge priority reg repeat return signed struct task typedef unique unsigned while wire xor
    """.split(),
)
# Comments that are directives of tools, not code
DIRECTIVES = re.compile(r"^\s*(synopsys|synthesis|pragma|verilator|spyglass|lint_off|lint_on|coverage|cadence|xilinx|altera)\b", re.IGNORECASE)
ENDINGS = re.compile(r"(;|\b(begin|end|endcase|endmodule|endfunction|endtask|endgenerate|else))\s*$")
WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_$]*")
LITERAL = re.compile(r"\d*'[sS]?[bBoOdDhH][0-9a-fA-F_xXzZ?]+|\"[^\"]*\"")
CODE_SYMBOL = re.compile(r"<=|==|!=|=|\(|\[|~|&|\||\^|\?")
# The text of a comment, inside a module and inside a procedural block: code parses in one of them
WRAPPERS = ("module mhsg_comment;\n{}\nendmodule\n", "module mhsg_comment;\nalways_comb begin\n{}\nend\nendmodule\n")


class rule_008(structure.Rule):
    """
    This rule checks for comments which contain commented-out code. A line comment on a line of its own is reported
    if it ends like a statement or declaration, with a semicolon or a keyword such as begin, end or else, it parses as
    SystemVerilog, as a module item or a statement, and its words are keywords or names used in the code of the file;
    with a symbol of code, such as =, <= or (, half of its words are enough, as commented-out code can name what was
    removed. Comments written as sentences do not parse, and directives of tools, such as synopsys or verilator
    comments, are not reported. It is disabled by default; the do254_plus rule set enables it (DEAD).

    .. NOTE:: This rule only reports the comments: deciding whether to delete them is left to the user.

    **Violation**

    .. code-block:: systemverilog

       // Wait for the FIFO to empty
       // if (rd_en) data_q <= data_d;
       if (empty) data_q <= '0;

    **Fix**

    .. code-block:: systemverilog

       // Wait for the FIFO to empty
       if (empty) data_q <= '0;
    """

    def __init__(self):
        super().__init__()
        self.languages = language.VERILOG_LANGUAGES
        self.disable = True
        self.fixable = False
        self.solution = "Remove commented-out code"
        self.configuration_documentation_link = None

    def _get_tokens_of_interest(self, oFile):
        setWords = code_words(oFile)
        lReturn = []
        for oToi in oFile.get_tokens_at_beginning_of_line_matching([parser.comment]):
            sValue = oToi.get_tokens()[-1].get_value() or ""
            if sValue.startswith("//") and is_commented_out_code(sValue[2:], setWords):
                lReturn.append(oToi)
        return lReturn

    def _analyze(self, lToi):
        for oToi in lToi:
            self.add_violation(violation.New(oToi.get_line_number(), oToi, self.solution))


def code_words(oFile):
    """The words of the code of a file, outside comments."""
    setReturn = set()
    for oToken in oFile.lAllObjects:
        if isinstance(oToken, (parser.comment, parser.whitespace, parser.carriage_return, parser.blank_line)):
            continue
        sValue = oToken.get_value()
        if sValue:
            setReturn.update(WORD.findall(sValue))
    return setReturn


def is_commented_out_code(sText, setCodeWords):
    sText = sText.split("//")[0].strip()
    if not sText or DIRECTIVES.match(sText) or not ENDINGS.search(sText):
        return False
    lWords = WORD.findall(LITERAL.sub(" ", sText))
    if not lWords:
        return False
    iKnown = sum(1 for s in lWords if s in KEYWORDS or s in setCodeWords)
    if iKnown < len(lWords) and not (CODE_SYMBOL.search(sText) and 2 * iKnown >= len(lWords)):
        return False
    return any(not SyntaxTree.fromText(s.format(sText)).diagnostics for s in WRAPPERS)
