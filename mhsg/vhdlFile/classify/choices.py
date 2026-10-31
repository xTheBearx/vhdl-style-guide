# -*- coding: utf-8 -*-

from mhsg.token import choices as token
from mhsg.vhdlFile import utils
from mhsg.vhdlFile.classify import choice


def classify_until(lUntils, iToken, lObjects):
    """
    choices ::=
        choice { | choice }
    """
    iCurrent = iToken
    iLast = 0
    lMyUntils = lUntils
    lMyUntils.append("|")

    while iLast != iCurrent:
        iLast = iCurrent
        iCurrent = choice.classify_until(lMyUntils, iCurrent, lObjects)
        iCurrent = utils.assign_next_token_if("|", token.bar, iCurrent, lObjects)

    return iCurrent
