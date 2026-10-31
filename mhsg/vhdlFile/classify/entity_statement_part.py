# -*- coding: utf-8 -*-

from mhsg.vhdlFile import utils
from mhsg.vhdlFile.classify import entity_statement


def detect(iToken, lObjects):
    """
    entity_statement_part ::=
        { entity_statement }
    """

    return utils.detect_submodule(iToken, lObjects, entity_statement)
