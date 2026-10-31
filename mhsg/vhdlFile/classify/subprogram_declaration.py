# -*- coding: utf-8 -*-

from mhsg.token import subprogram_declaration as token
from mhsg.vhdlFile import utils
from mhsg.vhdlFile.classify import subprogram_specification


def detect(iToken, lObjects):
    """
    subprogram_declaration ::=
        subprogram_specification ;
    """

    iCurrent = subprogram_specification.detect(iToken, lObjects)
    if iCurrent != iToken:
        if utils.is_next_token(";", iCurrent, lObjects):
            return utils.assign_next_token_required(";", token.semicolon, iCurrent, lObjects)
    return iCurrent
