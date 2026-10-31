# -*- coding: utf-8 -*-

from mhsg.token import association_list as token
from mhsg.vhdlFile import utils
from mhsg.vhdlFile.classify import association_element


def classify(iToken, lObjects):
    """
    association_list ::=
        association_element { , association_element }
    """
    iCurrent = association_element.detect(iToken, lObjects)

    while utils.is_next_token(",", iCurrent, lObjects):
        iCurrent = utils.assign_next_token_required(",", token.comma, iCurrent, lObjects)
        iCurrent = association_element.detect(iCurrent, lObjects)

    return iCurrent
