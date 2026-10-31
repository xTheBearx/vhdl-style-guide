# -*- coding: utf-8 -*-

from mhsg.token import interface_incomplete_type_declaration as token
from mhsg.vhdlFile import utils
from mhsg.vhdlFile.classify import identifier, incomplete_type_definition


def detect(iToken, lObjects):
    """
    interface_incomplete_type_declaration ::=
        type identifier [ is incomplete_type_definition ]
    """
    if utils.is_next_token("type", iToken, lObjects):
        return classify(iToken, lObjects)
    return iToken


def classify(iToken, lObjects):
    iCurrent = utils.assign_next_token_if("type", token.type_keyword, iToken, lObjects)
    iCurrent = identifier.classify(iCurrent, lObjects, token.identifier)
    if utils.is_next_token("is", iCurrent, lObjects):
        iCurrent = utils.assign_next_token_required("is", token.is_keyword, iCurrent, lObjects)
        iCurrent = incomplete_type_definition.classify(iCurrent, lObjects)

    return iCurrent
