# -*- coding: utf-8 -*-

from mhsg.vhdlFile import utils
from mhsg.vhdlFile.classify import entity_declarative_item


def detect(iToken, lObjects):
    """
    entity_declarative_part ::=
        { entity_declarative_item }
    """

    return utils.detect_submodule(iToken, lObjects, entity_declarative_item)
