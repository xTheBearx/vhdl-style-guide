# -*- coding: utf-8 -*-

import importlib

from mhsg import block_rule, parser, violation
from mhsg.vhdlFile import utils

# mhsg.rules exports the class line_length under the name of its module
line_length = importlib.import_module("mhsg.rules.line_length")


class rule_003(block_rule.Rule):
    """
    This rule checks the block comment footer is correct.

    |configuring_block_comments_link|

    **Violation**

    .. code-block:: vhdl

       --+-------------[ Header ]==============
       --|  Comment
       --|  Comment
       ----------------------------------------

    **Fix**

    .. code-block:: vhdl

       --+-------------[ Header ]==============
       --|  Comment
       --|  Comment
       --+--------------------------[ Footer ]=
    """

    def __init__(self):
        super().__init__()
        self.footer_left = None
        self.footer_left_repeat = "-"
        self.footer_string = None
        self.footer_right_repeat = None
        self.footer_alignment = "center"
        # The same as the line length of length_001
        self.max_footer_column = line_length.DEFAULT_LENGTH
        self.configuration.extend(["footer_left", "footer_left_repeat", "footer_string", "footer_right_repeat", "footer_alignment", "max_footer_column"])

    def analyze_comments(self, oToi):
        iLine, lTokens = utils.get_toi_parameters(oToi)
        iComments = utils.count_token_types_in_list_of_tokens(parser.comment, lTokens)

        iComment = 0
        for oToken in lTokens:
            iLine = utils.increment_line_number(iLine, oToken)
            iComment = utils.increment_comment_counter(iComment, oToken)

            if last_comment(iComment, iComments):
                analyze_footer(self, oToken, iLine, oToi)


def last_comment(iComment, iComments):
    if iComment == iComments:
        return True
    return False


def analyze_footer(self, oToken, iLine, oToi):
    sFooter = self.build_footer(oToken)
    sComment = oToken.get_value()

    if block_rule.is_footer(sComment):
        self.set_token_indent(oToken)
        if sComment != sFooter:
            sSolution = "Change block comment footer to : " + sFooter
            oViolation = violation.New(iLine, oToi, sSolution)
            self.add_violation(oViolation)
