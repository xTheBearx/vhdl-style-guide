# -*- coding: utf-8 -*-

from mhsg.vhdlFile import utils
from mhsg.vhdlFile.classify import protected_type_body_declarative_item


def detect(iToken, lObjects):
    """
    protected_type_body_declarative_part ::=
        { protected_type_body_declarative_item }
    """

    return utils.detect_submodule(iToken, lObjects, protected_type_body_declarative_item)
