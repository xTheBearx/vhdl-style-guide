# -*- coding: utf-8 -*-

from mhsg.token import parameter_specification as token
from mhsg.vhdlFile import utils
from mhsg.vhdlFile.classify import discrete_range


def classify_until(lUntils, iToken, lObjects):
    """
    parameter_specification ::=
        identifier in discrete_range
    """

    iCurrent = utils.assign_next_token(token.identifier, iToken, lObjects)
    iCurrent = utils.assign_next_token_required("in", token.in_keyword, iCurrent, lObjects)

    iCurrent = discrete_range.classify_until(lUntils, iCurrent, lObjects)

    return iCurrent
