# -*- coding: utf-8 -*-

from mhsg import parser
from mhsg.token import attribute_name as token
from mhsg.vhdlFile import utils
from mhsg.vhdlFile.classify import expression, signature


def detect(iToken, lObjects):
    """
    attribute_name ::=
        prefix [ signature ] ' attribute_designator [ ( expression ) ]
    """

    # Skip over prefix
    iCurrent = utils.find_next_token(iToken, lObjects)
    iCurrent = utils.find_next_token(iCurrent + 1, lObjects)

    while True:
        if utils.token_is_open_parenthesis(iCurrent, lObjects):
            iCurrent += 1
            iCurrent = utils.skip_tokens_until_matching_closing_paren(iCurrent, lObjects)
            iCurrent = utils.find_next_token(iCurrent + 1, lObjects)
        elif token_is_selected_suffix(iCurrent, lObjects):
            iCurrent = utils.find_next_token(iCurrent + 1, lObjects)
        else:
            break

    # Check for signature
    if utils.is_next_token("[", iCurrent, lObjects):
        return True

    # Check for tic
    if utils.is_next_token("'", iCurrent, lObjects):
        return True

    return False


def classify(iToken, lObjects):
    iCurrent = utils.assign_next_token(token.name, iToken, lObjects)

    while True:
        iCurrent = utils.find_next_token(iCurrent, lObjects)
        if utils.token_is_open_parenthesis(iCurrent, lObjects):
            iCurrent = utils.assign_token(lObjects, iCurrent, parser.open_parenthesis)
            iCurrent = utils.assign_tokens_until_matching_closing_paren(parser.todo, iCurrent, lObjects)
            iCurrent = utils.assign_token(lObjects, iCurrent, parser.close_parenthesis)
        elif token_is_selected_suffix(iCurrent, lObjects):
            iCurrent = utils.assign_next_token(parser.todo, iCurrent, lObjects)
        else:
            break

    signature.detect(iCurrent, lObjects)

    iCurrent = utils.assign_next_token_required("'", token.tic, iCurrent, lObjects)
    iCurrent = utils.assign_next_token(token.attribute, iCurrent, lObjects)

    return iCurrent


def token_is_selected_suffix(iToken, lObjects):
    sValue = lObjects[iToken].get_value()
    return len(sValue) > 1 and sValue.startswith(".")
