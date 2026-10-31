# -*- coding: utf-8 -*-

from mhsg import parser, violation
from mhsg.rules import tokens_of_interest as toi
from mhsg.vhdlFile import utils


def add_new_line(oToi):
    iToken = oToi.get_meta_data("iToken")

    oToi.set_meta_data("iStart", iToken)
    oToi.set_meta_data("sSolution", "Move parenthesis to next line.")
    oToi.set_meta_data("sAction", "add_new_line")
    toi.adjust_start_index_based_on_whitespace(oToi, -1)
    oViolation = _create_violation(oToi)
    return oViolation


def add_new_line_after(oToi):
    iToken = oToi.get_meta_data("iToken")
    lTokens = oToi.get_tokens()

    oToi.set_meta_data("iStart", iToken + 1)
    oToi.set_meta_data("sSolution", "Add new line after " + lTokens[iToken].get_value())
    oToi.set_meta_data("sAction", "add_new_line")
    oToi.set_meta_data("iToken", iToken + 2)
    oViolation = _create_violation(oToi)
    return oViolation


def remove_new_line(self, oToi):
    iToken = oToi.get_meta_data("iToken")
    lTokens = oToi.get_tokens()

    oToi.set_meta_data("sSolution", "Move parenthesis to previous line.")
    oToi.set_meta_data("sAction", "remove_new_line")
    iStart = utils.find_previous_non_whitespace_token(iToken - 1, lTokens) + 1
    oToi.set_meta_data("iStart", iStart)
    if _comment_in_range(lTokens, iStart, iToken):
        # Include the rest of the line so the comment can be moved after the code that joins its line
        oToi.set_meta_data("sAction", "remove_new_line_before_comment")
        oToi.set_meta_data("iToken", _get_index_of_end_of_line(lTokens, iToken))
    oViolation = _create_violation(oToi)
    return oViolation


def _comment_in_range(lTokens, iStart, iEnd):
    for oToken in lTokens[iStart:iEnd]:
        if isinstance(oToken, parser.comment):
            return True
    return False


def _get_index_of_end_of_line(lTokens, iToken):
    iReturn = iToken
    for iIndex in range(iToken + 1, len(lTokens)):
        if isinstance(lTokens[iIndex], parser.carriage_return):
            break
        iReturn = iIndex
    return iReturn


def remove_new_line_after(self, oToi):
    iToken = oToi.get_meta_data("iToken")
    lTokens = oToi.get_tokens()

    oToi.set_meta_data("sSolution", "Remove new line after " + lTokens[iToken].get_value())
    oToi.set_meta_data("sAction", "remove_new_line")
    oToi.set_meta_data("iStart", iToken + 1)
    oToi.set_meta_data("iToken", utils.find_next_non_whitespace_token(iToken + 1, lTokens))
    oViolation = _create_violation(oToi)
    return oViolation


def _create_violation(oToi):
    iStartIndex = oToi.get_meta_data("iStart")
    iStartLine = oToi.get_meta_data("iStartLine")
    iEndIndex = oToi.get_meta_data("iToken")
    sSolution = oToi.get_meta_data("sSolution")
    sAction = oToi.get_meta_data("sAction")

    dAction = _create_action_dictionary(sAction)
    oViolation = violation.New(iStartLine, oToi.extract_tokens(iStartIndex, iEndIndex), sSolution)
    oViolation.set_action(dAction)
    return oViolation


def _create_action_dictionary(sAction):
    dReturn = {}
    dReturn["action"] = sAction
    return dReturn
