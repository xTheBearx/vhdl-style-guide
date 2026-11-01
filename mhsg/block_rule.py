# -*- coding: utf-8 -*-

import string

from mhsg import parser
from mhsg.rule_group import structure
from mhsg.rules import utils as rules_utils
from mhsg.vhdlFile import utils


class Rule(structure.Rule):
    def __init__(self):
        super().__init__()
        self.fixable = False
        self.disable = True

        self.min_height = 3
        self.configuration.append("min_height")
        self.allow_indenting = "yes"
        self.configuration.append("allow_indenting")
        # Options set by the block comment rules which use them
        self.comment_left = None
        self.footer_left = None
        self.footer_left_repeat = None
        self.footer_string = None
        self.footer_right_repeat = None
        self.footer_alignment = None
        self.max_footer_column = None
        self.configuration_documentation_link = "configuring_block_comments_link"

    def analyze(self, oFile):
        self.allow_indenting = utils.convert_yes_no_option_to_boolean(self.allow_indenting)
        super().analyze(oFile)

    def analyze_comments(self, oToi):
        """
        Checks one block comment. Each block comment rule checks a different part of the block.
        """

    def _get_tokens_of_interest(self, oFile):
        lToi = oFile.get_consecutive_lines_starting_with_token(parser.comment, self.min_height)
        lReturn = []
        for oToi in lToi:
            iLeft, iLines, iRight = adjust_for_code_tags(oToi)
            if iLines >= self.min_height:
                lReturn.append(oToi.extract_tokens(iLeft, iRight))
        return lReturn

    def _analyze(self, lToi):
        for oToi in lToi:
            if not first_comment_is_a_header(oToi):
                continue

            self.analyze_comments(oToi)

    def fix(self, oFile, dFixOnly=None):
        """
        Applies fixes for any rule violations.
        """
        self.analyze(oFile)

    def set_token_indent(self, oToken):
        oToken.is_block_comment = True
        if not self.allow_indenting:
            oToken.set_indent(0)
            oToken.block_comment_indent = 0
        elif oToken.block_comment_scope_indent is not None:
            # Match the indent the indent pass gives a block comment, so analysis agrees with a fix run
            oToken.set_indent(oToken.block_comment_scope_indent)

    def calculate_leading_whitespace(self, oToken):
        if self.allow_indenting:
            iWhitespace = self.indent_size * get_block_comment_indent(oToken)
        else:
            iWhitespace = 0
        return iWhitespace

    def build_footer(self, oToken):
        iWhitespace = self.calculate_leading_whitespace(oToken)
        sFooter = "--"
        if self.footer_left is not None:
            sFooter += self.footer_left
            iFooter_left = len(self.footer_left)
        else:
            iFooter_left = 0

        if self.footer_string is None:
            sFooter += self.footer_left_repeat * (self.max_footer_column - iWhitespace - len(sFooter))
        elif self.footer_alignment == "center":
            iLength = int((self.max_footer_column - iWhitespace - len(self.footer_string)) / 2) - iFooter_left - 2
            sFooter += self.footer_left_repeat * (iLength)
            sFooter += self.footer_string
            sFooter += self.footer_right_repeat * (self.max_footer_column - len(sFooter))
        elif self.footer_alignment == "left":
            sFooter += self.footer_left_repeat
            sFooter += self.footer_string
            sFooter += self.footer_right_repeat * (self.max_footer_column - len(sFooter))
        elif self.footer_alignment == "right":
            iLength = self.max_footer_column - iWhitespace - len(sFooter) - len(self.footer_string) - 1
            sFooter += self.footer_left_repeat * (iLength)
            sFooter += self.footer_string
            sFooter += self.footer_right_repeat
        return sFooter

    def build_comment(self, oToken):
        sHeader = "--"
        sHeader += self.comment_left
        return sHeader


def is_header(sComment):
    if bare_comment(sComment):
        return False
    if not third_character_is_alphanumeric(sComment):
        return False
    return fourth_character_is_alphanumeric(sComment)


def fourth_character_is_alphanumeric(sComment):
    try:
        if sComment[3] not in string.punctuation:
            return False
    except IndexError:
        return True
    return True


def third_character_is_alphanumeric(sComment):
    if sComment[2] not in string.punctuation:
        return False
    if sComment[2] == "!":
        return False
    return True


def bare_comment(sString):
    if sString == "--":
        return True
    return False


def is_footer(sComment):
    return is_header(sComment)


def first_comment_is_a_header(oToi):
    oToken = oToi.get_first_token_matching(parser.comment)
    if is_header(oToken.get_value()):
        return True
    return False


def adjust_for_code_tags(oToi):
    lTokens = oToi.get_tokens()
    iLeft, iLines, iRight = extract_initial_indexes_from_token_list(lTokens)
    iLeft, iLines = adjust_indexes_for_code_tags_at_beginning_of_block_comment(lTokens, iLeft, iLines)
    iRight, iLines = adjust_indexes_for_code_tags_at_end_of_block_comment(lTokens, iRight, iLines)
    return iLeft, iLines, iRight


def extract_initial_indexes_from_token_list(lTokens):
    iLines = utils.count_carriage_returns(lTokens) + 1
    iLeft = 0
    iRight = len(lTokens)
    return iLeft, iLines, iRight


def adjust_indexes_for_code_tags_at_beginning_of_block_comment(lTokens, iLeft, iLines):
    if code_tag_detected(lTokens[0]):
        iLeft = 2
        iLines -= 1
    if code_tag_detected(lTokens[1]):
        iLeft = 3
        iLines -= 1
    return iLeft, iLines


def adjust_indexes_for_code_tags_at_end_of_block_comment(lTokens, iRight, iLines):
    if code_tag_detected(lTokens[-1]):
        if rules_utils.token_is_whitespace(lTokens[-2]):
            iRight = len(lTokens) - 4
        else:
            iRight = len(lTokens) - 3
        iLines -= 1
    return iRight, iLines


def code_tag_detected(oToken):
    for sTag in ["mhsg_on", "mhsg_off", "vsg_on", "vsg_off"]:
        if sTag in oToken.get_value():
            return True
    return False


def get_block_comment_indent(oToken):
    """
    Returns the indent of a comment when it is treated as a block comment.
    """
    if oToken.block_comment_scope_indent is not None:
        return oToken.block_comment_scope_indent
    return oToken.get_indent()
