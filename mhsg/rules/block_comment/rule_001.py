# -*- coding: utf-8 -*-

import importlib
import math

from mhsg import block_rule, parser, violation
from mhsg.vhdlFile import utils

# mhsg.rules exports the class line_length under the name of its module
line_length = importlib.import_module("mhsg.rules.line_length")


class rule_001(block_rule.Rule):
    """
    This rule checks the block comment header is correct.

    |configuring_block_comments_link|

    **Violation**

    .. code-block:: vhdl

       ----------------------------------------
       --   Comment
       --   Comment
       ----------------------------------------

    **Fix**

    .. code-block:: vhdl

       --+-------------[ Header ]==============
       --   Comment
       --   Comment
       ----------------------------------------
    """

    def __init__(self):
        super().__init__()
        self.header_left = None
        self.header_left_repeat = "-"
        self.header_string = None
        self.header_right_repeat = None
        self.header_alignment = "center"
        # The same as the line length of length_001
        self.max_header_column = line_length.DEFAULT_LENGTH
        self.configuration.extend(["header_left", "header_left_repeat", "header_string", "header_right_repeat", "header_alignment", "max_header_column"])

    def analyze(self, oFile):
        self.allow_indenting = utils.convert_yes_no_option_to_boolean(self.allow_indenting)

        self._print_debug_message("Analyzing rule: " + self.unique_id)
        lToi = self._get_tokens_of_interest(oFile)

        for oToi in lToi:
            lTokens = oToi.get_tokens()

            if not self.allow_indenting:
                iWhitespace = 0
            elif isinstance(lTokens[0], parser.comment):
                iWhitespace = self.indent_size * block_rule.get_block_comment_indent(lTokens[0])
            else:
                iWhitespace = self.indent_size * block_rule.get_block_comment_indent(lTokens[1])

            sHeader = "--"

            if self.header_left is not None:
                sHeader += self.header_left
                iHeader_left = len(self.header_left)
            else:
                iHeader_left = 0

            if self.header_string is None:
                sHeader += self.header_left_repeat * (self.max_header_column - iWhitespace - len(sHeader))
            elif self.header_alignment == "center":
                iLeft = math.floor((self.max_header_column - iWhitespace - len(self.header_string)) / 2) - iHeader_left - 2
                sLeft = self.header_left_repeat * iLeft
                iRight = self.max_header_column - iWhitespace - 2 - iHeader_left - len(self.header_string) - iLeft
                sRight = self.header_right_repeat * iRight
                sHeader += sLeft + self.header_string + sRight
            elif self.header_alignment == "left":
                sHeader += self.header_left_repeat
                sHeader += self.header_string
                iLength = self.max_header_column - iWhitespace - len(sHeader)
                sHeader += self.header_right_repeat * iLength
            elif self.header_alignment == "right":
                iLength = self.max_header_column - iWhitespace - len(sHeader) - len(self.header_string) - 1
                sHeader += self.header_left_repeat * iLength
                sHeader += self.header_string
                sHeader += self.header_right_repeat

            for oToken in lTokens:
                if isinstance(oToken, parser.comment):
                    sComment = oToken.get_value()
                    try:
                        if block_rule.is_header(sComment):
                            self.set_token_indent(oToken)
                            if sComment != sHeader:
                                sSolution = "Change block comment header to : " + sHeader
                                oViolation = violation.New(oToi.get_line_number(), oToi, sSolution)
                                self.add_violation(oViolation)
                        break
                    except IndexError:
                        break


#         1         2         3         4         5         6         7         8
# -------------------------------<-    80 chars    ->-----------------------------
# ------------------------------<-    80 chars    ->------------------------------
