# -*- coding: utf-8 -*-

import re

from mhsg import parser, severity, token, violation
from mhsg.rule_group import structure
from mhsg.rules.reserved.rule_001 import dMap

# Every reserved word of every VHDL standard
lReservedWords = {sWord for lWords in dMap.values() for sWord in lWords}

# Names from the standard and IEEE packages, which commented out code often uses even if the code does not
lStandardNames = {
    "bit",
    "bit_vector",
    "boolean",
    "character",
    "integer",
    "natural",
    "positive",
    "real",
    "signed",
    "std_logic",
    "std_logic_vector",
    "std_ulogic",
    "std_ulogic_vector",
    "string",
    "time",
    "unsigned",
    "rising_edge",
    "falling_edge",
    "resize",
    "to_integer",
    "to_signed",
    "to_unsigned",
    "ieee",
    "std",
    "work",
}

# A statement or declaration ends with a semicolon or with one of these keywords
lEndingKeywords = ["then", "else", "begin", "is", "loop", "generate"]

reWord = re.compile(r"[a-z][a-z0-9_]*")
reBitString = re.compile(r'[a-z0-9]*"[^"]*"')
reCharacter = re.compile(r"'.'")
reAttribute = re.compile(r"'[a-z][a-z0-9_]*")
# Only the prefix of a selected name, such as ieee in ieee.numeric_std.all, needs to be known
reSuffix = re.compile(r"\.[a-z][a-z0-9_]*")
# Symbols which appear in code but rarely in sentences
reCodeSymbol = re.compile(r"<=|:=|=>|=|:|\(|'|\"")


class rule_013(structure.Rule):
    """
    This rule checks for comments which contain commented out code.

    A comment on a line of its own is reported if it ends like a statement or declaration, with a semicolon or one of the keywords **then**, **else**, **begin**, **is**, **loop** or **generate**, and its words are VHDL reserved words, common names from the standard and IEEE packages, or names used in the code of the file.
    If the comment contains a symbol used in code, such as **<=**, **:=**, **=** or **(**, half of its words are enough, because commented out code can name things which were removed from the code.
    Comments written as sentences are not reported, because they contain words which are not in the code.

    .. NOTE:: This rule is disabled by default.
       It only reports the comments, because deciding whether to delete them is left to the user.

    **Violation**

    .. code-block:: vhdl

       -- use ieee.numeric_std.all;

       -- Wait for the FIFO to empty
       -- if rd_en = '1' then
       if empty = '1' then

    **Fix**

    .. code-block:: vhdl

       -- Wait for the FIFO to empty
       if empty = '1' then
    """

    def __init__(self):
        super().__init__()
        self.solution = "Remove commented out code."
        self.disable = True
        self.fixable = False
        self.severity = severity.warning("Warning")
        self.configuration_documentation_link = None

    def _get_tokens_of_interest(self, oFile):
        lCodeWords = get_code_words(oFile)
        lReturn = []
        for oToi in oFile.get_tokens_at_beginning_of_line_matching([parser.comment]):
            oComment = oToi.get_tokens()[-1]
            if isinstance(oComment, token.pragma.pragma):
                continue
            if is_commented_out_code(oComment.get_value(), lCodeWords):
                lReturn.append(oToi)
        return lReturn

    def _analyze(self, lToi):
        for oToi in lToi:
            oViolation = violation.New(oToi.get_line_number(), oToi, self.solution)
            self.add_violation(oViolation)


def get_code_words(oFile):
    """
    Returns the lower case words used in the code of the file, outside of comments.
    """
    lReturn = set()
    for oToken in oFile.lAllObjects:
        if isinstance(oToken, (parser.comment, parser.whitespace, parser.carriage_return, parser.blank_line)):
            continue
        sValue = oToken.get_value()
        if sValue is None:
            continue
        lReturn.update(reWord.findall(sValue.lower()))
    return lReturn


def is_commented_out_code(sComment, lCodeWords):
    sText = sComment.lower()
    if sText.startswith("--"):
        sText = sText[2:]
    # An inline comment inside the commented out code
    sText = sText.split("--")[0].strip()
    if len(sText) == 0 or not ends_like_code(sText):
        return False
    bCodeSymbol = reCodeSymbol.search(sText) is not None
    sText = reBitString.sub(" ", sText)
    sText = reCharacter.sub(" ", sText)
    sText = reAttribute.sub(" ", sText)
    sText = reSuffix.sub(" ", sText)
    lWords = reWord.findall(sText)
    if len(lWords) == 0:
        return False
    iKnown = len([sWord for sWord in lWords if sWord in lReservedWords or sWord in lStandardNames or sWord in lCodeWords])
    if iKnown == len(lWords):
        return True
    # Commented out code can name things which were removed from the code, such as an old signal
    return bCodeSymbol and iKnown * 2 >= len(lWords)


def ends_like_code(sText):
    if sText.endswith(";"):
        return True
    for sKeyword in lEndingKeywords:
        if re.search(rf"\b{sKeyword}$", sText):
            return True
    return False
