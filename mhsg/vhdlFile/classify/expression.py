# -*- coding: utf-8 -*-

from mhsg import parser
from mhsg.vhdlFile import utils
from mhsg.vhdlFile.classify import bit_string_literal, external_name


def classify(iToken, lObjects):
    """
    expression ::=
        condition_operator primary
      | logical_expression
    """
    return utils.assign_token(lObjects, iToken, parser.todo)


def classify_until(lUntils, iToken, lObjects, oType=parser.todo):
    """
    expression ::=
        condition_operator primary
      | logical_expression
    """
    iCurrent = iToken
    iStop = len(lObjects) - 1
    iOpenParenthesis = 0
    iCloseParenthesis = 0
    iPrevious = 0
    while iCurrent < iStop:
        if iCurrent == iPrevious:
            break
        iPrevious = iCurrent
        iCurrent = utils.find_next_token(iCurrent, lObjects)
        if utils.token_is_open_parenthesis(iCurrent, lObjects):
            iOpenParenthesis += 1
        if utils.token_is_close_parenthesis(iCurrent, lObjects):
            iCloseParenthesis += 1

        if iOpenParenthesis < iCloseParenthesis:
            break
        elif lObjects[iCurrent].get_lower_value() in lUntils:
            if utils.token_is_close_parenthesis(iCurrent, lObjects):
                # A close parenthesis ending the expression was handled above, so this one closes a nested parenthesis
                utils.assign_token(lObjects, iCurrent, parser.close_parenthesis)
                iCurrent += 1
                continue
            elif utils.token_is_comma(iCurrent, lObjects):
                if iOpenParenthesis == iCloseParenthesis:
                    break
                else:
                    utils.assign_token(lObjects, iCurrent, parser.comma)
                    iCurrent += 1
            else:
                break
        else:
            iPrevious = iCurrent
            for oToken in [external_name, bit_string_literal]:
                if iPrevious == iCurrent:
                    iCurrent = oToken.detect(iCurrent, lObjects)

            if iPrevious == iCurrent:
                utils.assign_special_tokens(lObjects, iCurrent, oType)
                iCurrent += 1
    return iCurrent
