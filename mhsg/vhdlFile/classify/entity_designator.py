# -*- coding: utf-8 -*-

from mhsg.token import entity_designator as token
from mhsg.vhdlFile import utils
from mhsg.vhdlFile.classify import signature


def classify(iToken, lObjects):
    """
    entity_designator ::=
        entity_tag [ signature ]
    """

    iCurrent = utils.assign_next_token(token.entity_tag, iToken, lObjects)

    iCurrent = signature.detect(iCurrent, lObjects)

    return iCurrent
