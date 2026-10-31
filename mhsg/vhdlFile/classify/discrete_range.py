# -*- coding: utf-8 -*-

from mhsg import parser
from mhsg.token import range_constraint
from mhsg.vhdlFile import utils
from mhsg.vhdlFile.classify import (  # pylint: disable=redefined-builtin
    range,
    subtype_indication,
)


def detect(iToken, lObjects):
    """
    discrete_range ::=
        *discrete*_subtype_indication | range
    """
    if subtype_indication_with_constraint_ends_discrete_range(iToken, lObjects):
        return subtype_indication.classify(iToken, lObjects)
    return range.detect(iToken, lObjects)


def classify(iToken, lObjects):
    """
    discrete_range ::=
        *discrete*_subtype_indication | range
    """

    return utils.assign_token(lObjects, iToken, parser.todo)


def classify_until(lUntils, iToken, lObjects):
    iCurrent = iToken
    iStop = len(lObjects) - 1
    iOpenParenthesis = 0
    iCloseParenthesis = 0
    iPrevious = -1

    while iCurrent < iStop:
        iCurrent = utils.find_next_token(iCurrent, lObjects)

        if iCurrent == iPrevious:
            utils.print_missing_error_message(lUntils, iToken, lObjects)

        if utils.token_is_open_parenthesis(iCurrent, lObjects):
            iOpenParenthesis += 1
        if utils.token_is_close_parenthesis(iCurrent, lObjects):
            iCloseParenthesis += 1
        if iOpenParenthesis < iCloseParenthesis:
            break
        elif iOpenParenthesis == iCloseParenthesis:
            if lObjects[iCurrent].get_lower_value() in lUntils:
                break
            elif utils.is_next_token("'", iToken, lObjects):
                # Ensure that range attributes are not misidentified as range keywords.
                utils.assign_token(lObjects, iCurrent, parser.todo)
                iCurrent = utils.find_next_token(iCurrent, lObjects)
                utils.assign_token(lObjects, iCurrent, parser.todo)
            elif utils.is_next_token("range", iToken, lObjects):
                utils.assign_token(lObjects, iCurrent, range_constraint.range_keyword)
            else:
                utils.assign_token(lObjects, iCurrent, parser.todo)
        else:
            utils.assign_token(lObjects, iCurrent, parser.todo)
        iPrevious = iCurrent

    return iCurrent


def subtype_indication_with_constraint_ends_discrete_range(iToken, lObjects):
    # An indexed name followed by more of an expression, e.g. CONST(0) - 1 downto 0, is a range
    for sEnd in [")", ","]:
        if utils.are_next_consecutive_tokens([None, "(", None, ")", sEnd], iToken, lObjects):
            return True
    return False
