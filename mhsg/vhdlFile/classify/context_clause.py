# -*- coding: utf-8 -*-

from mhsg.vhdlFile import utils
from mhsg.vhdlFile.classify import context_item


def detect(iToken, lObjects):
    """
    context_clause ::=
        { context_item }
    """
    iCurrent = utils.detect_submodule(iToken, lObjects, context_item)
    return iCurrent
