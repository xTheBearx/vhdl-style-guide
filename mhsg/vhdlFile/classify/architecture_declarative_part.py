# -*- coding: utf-8 -*-

from mhsg.vhdlFile import utils
from mhsg.vhdlFile.classify import block_declarative_item


def detect(iToken, lObjects):
    """
    architecture_declarative_part ::=
        { block_declarative_item }
    """

    return utils.detect_submodule(iToken, lObjects, block_declarative_item)
